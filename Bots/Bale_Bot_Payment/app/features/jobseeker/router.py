from aiogram import Router
from app.features.jobseeker.create_resume.handlers import router as create_resume_handlers_router
from app.features.jobseeker.upload_resume.handlers import router as upload_resume_handlers_router

router = Router(name="jobseeker")
router.include_router(create_resume_handlers_router)
router.include_router(upload_resume_handlers_router)
