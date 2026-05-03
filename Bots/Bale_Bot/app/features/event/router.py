from aiogram import Router

from app.features.event.handlers import router as event_handlers_router

router = Router()
router.include_router(event_handlers_router)
