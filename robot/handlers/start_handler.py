from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from robot.utils import get_text_by_name, identify_user

start_router = Router()


@start_router.message(Command("start"))
async def start(message: Message):
    user, is_new = await identify_user(telegram_id=message.from_user.id)

    if is_new:
        await message.answer(await get_text_by_name("Начальный текст для нового пользователя", "Привет! Новый текст."))
    else:
        await message.answer(await get_text_by_name("Начальный текст для старого пользователя", "Привет! Старый текст."))
