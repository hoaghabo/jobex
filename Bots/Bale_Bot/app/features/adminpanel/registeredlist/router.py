from aiogram import Router

from app.features.adminpanel.registeredlist.handlers import router as registered_list_handlers_router


router = Router(name="registeredlist")
router.include_router(registered_list_handlers_router)
