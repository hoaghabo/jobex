from aiogram import Router
from app.features.company.creatjobpost.handlers import router as company_jobposts_handler_router

router = Router(name="company_jobposts")
router.include_router(company_jobposts_handler_router)
