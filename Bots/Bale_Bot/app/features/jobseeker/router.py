from aiogram import Router
from app.features.jobseeker.create_resume.handlers import router as create_resume_handlers_router

router = Router(name="jobseeker")
router.include_router(create_resume_handlers_router)
