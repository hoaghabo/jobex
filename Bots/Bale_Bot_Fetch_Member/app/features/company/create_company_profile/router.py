from aiogram import Router
from app.features.company.create_company_profile.handlers import router as company_profile_handler_router

router = Router(name="company_profile")
router.include_router(company_profile_handler_router)
