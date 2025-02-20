import os

from django.core.management.base import BaseCommand, CommandError

from aiogram import Dispatcher, Bot
from robot.handlers import router
import asyncio
import logging
from robot.schedulers.start_scheduler import start_scheduler


class Command(BaseCommand):
    help = 'RUN COMMAND: python manage.py runbot'

    def handle(self, *args, **options):
        bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        dp = Dispatcher()
        dp.include_router(router)

        if not os.path.exists('logs'):
            os.makedirs('logs')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler('logs/bot.log'),
                logging.StreamHandler()
            ]
        )

        async def main():
            start_scheduler(bot)
            await dp.start_polling(bot)

        asyncio.run(main())
