from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

control_accounts_router = Router()


@control_accounts_router.callback_query(F.data == "control_accounts")
async def control_accounts(callback : CallbackQuery):
    await callback.answer('')
    await callback.message.answer("Выберите опцию:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Вывести все аккаунты", callback_data="list_accounts")],
            [InlineKeyboardButton(text="Добавить аккаунт",
                                  callback_data="add_account")],
        ]
    ))
