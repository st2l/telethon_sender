from aiogram import Router, F
from aiogram.types import (CallbackQuery, Message, InlineKeyboardMarkup,
                           InlineKeyboardButton, FSInputFile)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from robot.models import TelegramAccount
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from asgiref.sync import sync_to_async
import os
import re
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

start_mailing_router = Router()


class MailingState(StatesGroup):
    select_account = State()
    upload_file = State()
    select_type = State()
    dm_range = State()
    group_range = State()
    delay = State()
    message_text = State()


@sync_to_async
def get_all_accounts():
    return list(TelegramAccount.objects.all())


@sync_to_async
def get_account(phone):
    return TelegramAccount.objects.get(phone=phone)


@start_mailing_router.callback_query(F.data == "start_mailing")
async def start_mailing_handler(callback: CallbackQuery, state: FSMContext):
    accounts = await get_all_accounts()

    if not accounts:
        await callback.message.answer(
            "Нет доступных аккаунтов для рассылки. Сначала добавьте аккаунт.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Добавить аккаунт", callback_data="add_account")],
                [InlineKeyboardButton(text="Назад", callback_data="start")]
            ])
        )
        return

    keyboard = []
    for account in accounts:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📱 {account.phone}", callback_data=f"mailing_account_{account.phone}")
        ])

    await callback.message.answer(
        "Выберите аккаунт для рассылки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(MailingState.select_account)
    await callback.answer()


@start_mailing_router.callback_query(F.data.startswith("mailing_account_"))
async def handle_account_selection(callback: CallbackQuery, state: FSMContext):
    phone = callback.data.split("mailing_account_")[1]
    await state.update_data(selected_account=phone)

    await callback.message.answer("Отправьте txt файл со списком ID (каждый ID с новой строки)")
    await state.set_state(MailingState.upload_file)
    await callback.answer()


@start_mailing_router.message(MailingState.upload_file)
async def handle_file_upload(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith('.txt'):
        await message.answer("Пожалуйста, отправьте txt файл")
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    await message.bot.download_file(file_path, "temp_ids.txt")

    await state.update_data(ids_file="temp_ids.txt")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправка в ЛС",
                              callback_data="mailing_type_dm")],
        [InlineKeyboardButton(text="Отправка в группы",
                              callback_data="mailing_type_group")],
        [InlineKeyboardButton(text="Отправка в ЛС и группы",
                              callback_data="mailing_type_both")]
    ])

    await message.answer("Выберите тип рассылки:", reply_markup=keyboard)
    await state.set_state(MailingState.select_type)


@start_mailing_router.callback_query(F.data.startswith("mailing_type_"))
async def handle_mailing_type(callback: CallbackQuery, state: FSMContext):
    mailing_type = callback.data.split("mailing_type_")[1]
    await state.update_data(mailing_type=mailing_type)

    if mailing_type == "dm":
        await callback.message.answer("Введите диапазон для ЛС (например: 1-100)")
        await state.set_state(MailingState.dm_range)
    elif mailing_type == "group":
        await callback.message.answer("Введите диапазон для групп (например: 1-100)")
        await state.set_state(MailingState.group_range)
    else:  # both
        await callback.message.answer("Введите диапазон для ЛС (например: 1-100)")
        await state.set_state(MailingState.dm_range)

    await callback.answer()


@start_mailing_router.message(MailingState.dm_range)
async def handle_dm_range(message: Message, state: FSMContext):
    if not re.match(r'^\d+-\d+$', message.text):
        await message.answer("Неверный формат. Используйте формат: число-число")
        return

    data = await state.get_data()
    await state.update_data(dm_range=message.text)

    if data['mailing_type'] == 'both':
        await message.answer("Введите диапазон для групп (например: 1-100)")
        await state.set_state(MailingState.group_range)
    else:
        await message.answer("Введите задержку между сообщениями (в секундах)")
        await state.set_state(MailingState.delay)


@start_mailing_router.message(MailingState.group_range)
async def handle_group_range(message: Message, state: FSMContext):
    if not re.match(r'^\d+-\d+$', message.text):
        await message.answer("Неверный формат. Используйте формат: число-число")
        return

    await state.update_data(group_range=message.text)
    await message.answer("Введите задержку между сообщениями (в секундах)")
    await state.set_state(MailingState.delay)


@start_mailing_router.message(MailingState.delay)
async def handle_delay(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число")
        return

    await state.update_data(delay=int(message.text))
    await message.answer("Введите текст для рассылки:")
    await state.set_state(MailingState.message_text)


@start_mailing_router.message(MailingState.message_text)
async def handle_message_text(message: Message, state: FSMContext):
    await state.update_data(message_text=message.text)
    data = await state.get_data()

    await message.answer(
        "Рассылка запущена!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Вернуться в главное меню", callback_data="start")]
        ])
    )

    # Here you would implement the actual mailing logic
    if data['mailing_type'] in ['dm', 'both']:
        await send_dm_messages(data)  # This function needs to be implemented

    if data['mailing_type'] in ['group', 'both']:
        # This function needs to be implemented
        await send_group_messages(data)

    # Cleanup
    if os.path.exists(data['ids_file']):
        os.remove(data['ids_file'])

    
    await state.clear()


async def send_dm_messages(data):
    """
    Send messages to users using Telethon client with PeerUser
    """
    logging.info("Starting DM mailing process")
    
    try:
        account = await get_account(data['selected_account'])
        phone = account.phone
        start_range, end_range = map(int, data['dm_range'].split('-'))
        delay = data['delay']
        message_text = data['message_text']
        
        with open(data['ids_file'], 'r') as f:
            all_ids = [line.strip() for line in f.readlines()]
        
        selected_ids = all_ids[start_range-1:end_range]
        
        client = TelegramClient(
            f"sessions/{phone}",
            os.getenv('TELEGRAM_API_ID'),
            os.getenv('TELEGRAM_API_HASH')
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            logging.error(f"Account {phone} is not authorized")
            await client.disconnect()
            return
        
        for user_id in selected_ids:
            try:
                # Clean up the input
                user_id = user_id.strip()
                
                # Try to get user entity based on input type
                try:
                    if user_id.isdigit():
                        # Numeric ID
                        entity = await client.get_entity(int(user_id))
                    elif user_id.startswith(('https://t.me/', 't.me/')):
                        # Handle t.me links
                        username = user_id.split('/')[-1]
                        entity = await client.get_entity(username)
                    elif user_id.startswith('@'):
                        # Handle @username
                        entity = await client.get_entity(user_id)
                    else:
                        # Try as username without @
                        entity = await client.get_entity(user_id)
                
                    await client.send_message(entity, message_text)
                    logging.info(f"Message sent to {user_id}")
                    await asyncio.sleep(delay)
                    
                except ValueError as e:
                    logging.error(f"Invalid user identifier: {user_id} - {str(e)}")
                    continue
                    
            except Exception as e:
                logging.error(f"Error sending message to {user_id}: {str(e)}")
                continue
        
        await client.disconnect()
        logging.info("DM mailing process completed")
        
    except Exception as e:
        logging.error(f"Error in send_dm_messages: {str(e)}")


async def send_group_messages(data):
    """
    Send messages to groups using Telethon client
    Handles both numeric IDs and group links/usernames
    """
    logging.info("Starting group mailing process")
    
    try:
        account = await get_account(data['selected_account'])
        phone = account.phone
        start_range, end_range = map(int, data['group_range'].split('-'))
        delay = data['delay']
        message_text = data['message_text']
        
        with open(data['ids_file'], 'r') as f:
            all_ids = [line.strip() for line in f.readlines()]
        
        selected_ids = all_ids[start_range-1:end_range]
        
        client = TelegramClient(
            f"sessions/{phone}",
            os.getenv('TELEGRAM_API_ID'),
            os.getenv('TELEGRAM_API_HASH')
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            logging.error(f"Account {phone} is not authorized")
            await client.disconnect()
            return
        
        for group_id in selected_ids:
            try:
                group_id = group_id.strip()
                
                # Handle different types of group identifiers
                try:
                    if group_id.isdigit():
                        # Numeric ID
                        entity = await client.get_entity(int(group_id))
                    elif group_id.startswith(('https://t.me/joinchat/', 't.me/joinchat/')):
                        # Private group invite link
                        invite_hash = group_id.split('/')[-1][1:]
                        await client(ImportChatInviteRequest(invite_hash))
                        entity = await client.get_entity(group_id)
                    elif group_id.startswith(('https://t.me/', 't.me/')):
                        # Public group link
                        try:
                            username = group_id.split('/')[-1]
                            await client(JoinChannelRequest(username))
                            entity = await client.get_entity(username)
                        except:
                            invite_hash = group_id.split('/')[-1].replace('+', '')
                            logging.info(f'Invite hash: {invite_hash}')
                            entity = await client(ImportChatInviteRequest(invite_hash))
                        
                        try:

                            invite_hash = group_id.split('/')[-1].replace('+', '')
                            link = f'https://t.me/joinchat/{invite_hash}'
                            logging.info(f'Invite hash: {invite_hash}')
                            entity = await client(ImportChatInviteRequest(link))

                        except Exception as e:
                            logging.error(f"Error joining group: {e}")
                            continue
                    elif group_id.startswith('@'):
                        # @username format
                        await client(JoinChannelRequest(group_id))
                        entity = await client.get_entity(group_id)
                    else:
                        # Try as username without @
                        await client(JoinChannelRequest(group_id))
                        entity = await client.get_entity(group_id)
                    
                    logging.info(f"Successfully joined group {group_id}")
                    await asyncio.sleep(2)  # Small delay after joining
                    
                    await client.send_message(entity, message_text)
                    logging.info(f"Message sent to group {group_id}")
                    await asyncio.sleep(delay)
                    
                except ValueError as e:
                    logging.error(f"Invalid group identifier: {group_id} - {str(e)}")
                    continue
                    
            except Exception as e:
                logging.error(f"Error processing group {group_id}: {str(e)}")
                continue
        
        await client.disconnect()
        logging.info("Group mailing process completed")
        
    except Exception as e:
        logging.error(f"Error in send_group_messages: {str(e)}")
