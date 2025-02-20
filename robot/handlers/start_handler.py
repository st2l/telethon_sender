from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from robot.utils import get_text_by_name, identify_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_router = Router()


@start_router.message(Command("start"))
async def start(message: Message):
    user, is_new = await identify_user(telegram_id=message.from_user.id)

    await message.answer("Выберите опцию:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Контроль аккаунтов",
                                  callback_data="control_accounts")],
            [InlineKeyboardButton(text="Начать рассылку",
                                  callback_data="start_mailing")],
        ]
    ))


@start_router.callback_query(F.data == "start")
async def start_(message: Message):
    await message.answer("Выберите опцию:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Контроль аккаунтов",
                                  callback_data="control_accounts")],
            [InlineKeyboardButton(text="Начать рассылку",
                                  callback_data="start_mailing")],
        ]
    ))
