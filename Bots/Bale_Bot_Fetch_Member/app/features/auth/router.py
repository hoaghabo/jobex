from aiogram import Router
from app.features.auth.handlers import router as auth_handlers_router

router = Router(name="auth")
router.include_router(auth_handlers_router)
