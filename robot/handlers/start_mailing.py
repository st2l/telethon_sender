from aiogram import Router, F
from aiogram.types import CallbackQuery

start_mailing_router = Router()

@start_mailing_router.callback_query(F.data == "start_mailing")
async def start_mailing_handler(callback: CallbackQuery):
    pass