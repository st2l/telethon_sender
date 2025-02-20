from aiogram import Router
from .start_handler import start_router
from .add_account import add_account_router
from .control_accounts import control_accounts_router
from .start_mailing import start_mailing_router

router = Router()

router.include_router(start_router)
router.include_router(add_account_router)
router.include_router(control_accounts_router)
router.include_router(start_mailing_router)