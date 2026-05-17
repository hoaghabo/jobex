from aiogram import Router
from app.features.company.my_company_profile.handlers import router as my_company_handler_router

router = Router(name="my_company_profile")
router.include_router(my_company_handler_router)
