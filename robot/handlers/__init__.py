from aiogram import Router
from .start_handler import start_router
router = Router()

router.include_router(start_router)