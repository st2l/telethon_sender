from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from robot.models import TelegramAccount
from asgiref.sync import sync_to_async
import os

list_accounts_router = Router()

@sync_to_async
def get_all_accounts():
    return list(TelegramAccount.objects.all())

@sync_to_async
def delete_account(phone: str):
    try:
        account = TelegramAccount.objects.get(phone=phone)
        # Delete session file
        session_path = f"sessions/{phone}.session"
        if os.path.exists(session_path):
            os.remove(session_path)
        # Delete from DB
        account.delete()
        return True
    except TelegramAccount.DoesNotExist:
        return False

@list_accounts_router.callback_query(F.data == "list_accounts")
async def list_accounts(callback: CallbackQuery):
    accounts = await get_all_accounts()
    
    if not accounts:
        await callback.message.answer(
            "Нет зарегистрированных аккаунтов", 
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Добавить аккаунт", callback_data="add_account")],
                    [InlineKeyboardButton(text="Назад", callback_data="control_accounts")]
                ]
            )
        )
        await callback.answer()
        return

    keyboard = []
    for account in accounts:
        keyboard.append([
            InlineKeyboardButton(text=f"📱 {account.phone}", callback_data=f"account_{account.phone}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"delete_account_{account.phone}")
        ])
    
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="control_accounts")])
    
    await callback.message.answer(
        "Список зарегистрированных аккаунтов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@list_accounts_router.callback_query(F.data.startswith("delete_account_"))
async def delete_account_handler(callback: CallbackQuery):
    phone = callback.data.split("delete_account_")[1]
    
    if await delete_account(phone):
        await callback.answer("Аккаунт успешно удален!")
        # Refresh the accounts list
        await list_accounts(callback)
    else:
        await callback.answer("Ошибка при удалении аккаунта!", show_alert=True)
