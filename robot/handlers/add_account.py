from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from telethon.sync import TelegramClient
import telethon
from robot.models import TelegramAccount
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import os
import logging

add_account_router = Router()
load_dotenv()

if not os.path.exists('sessions'):
    os.makedirs('sessions')


class AddAccountState(StatesGroup):
    phone = State()
    password = State()
    code = State()


@add_account_router.callback_query(F.data == "add_account")
async def add_account(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите номер телефона в международном формате\n(например: +79123456789)")
    await state.set_state(AddAccountState.phone)
    await callback.answer()


@add_account_router.message(AddAccountState.phone)
async def phone_handler(message: Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    await message.answer("Если у аккаунта есть 2FA введите код сюда:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Пропустить", callback_data="skip_password")]
        ]
    ))
    await state.set_state(AddAccountState.password)


@add_account_router.message(AddAccountState.password)
async def passwd_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    password = message.text
    await state.update_data(password=password)

    client = TelegramClient(
        f"sessions/{phone}", os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    await state.update_data(client=client)
    await client.connect()
    phone_code_hash = (await client.send_code_request(phone)).phone_code_hash
    await state.update_data(phone_code_hash=phone_code_hash)

    await message.answer("Введите код из смс:")
    await state.set_state(AddAccountState.code)


@add_account_router.callback_query(F.data == "skip_password")
async def skip_password(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    
    client = TelegramClient(
        f"sessions/{phone}", os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    await state.update_data(client=client)
    await client.connect()
    phone_code_hash = (await client.send_code_request(phone)).phone_code_hash
    await state.update_data(phone_code_hash=phone_code_hash)

    await callback.message.answer("Введите код из смс:")
    await state.set_state(AddAccountState.code)
    await callback.answer()


import re
@add_account_router.message(AddAccountState.code)
async def code_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    password = data.get('password', None)
    client = data.get('client')
    phone_code_hash = data.get('phone_code_hash')
    code = re.sub(r'\D', '', message.text)

    logging.info(f'Code -> {code}')
    logging.info(f'Password -> {password}')

    if password is None:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
    else:
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except:
            try:
                await client.sign_in(password=password)
            except Exception as e:
                logging.error(f'Error in password entering: {e}')

    await client.disconnect()
    await TelegramAccount.objects.aget_or_create(phone=phone)
    await message.answer("Аккаунт успешно добавлен", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить еще аккаунт", callback_data="add_account")],
            [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
        ]
    ))
    await state.clear()