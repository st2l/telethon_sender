from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

scheduler = AsyncIOScheduler()


def start_scheduler(bot):
    logging.info("Scheduler started")
    scheduler.start()
