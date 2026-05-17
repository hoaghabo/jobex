from aiogram import Router
from app.features.company.create_job_post.handlers import router as company_jobposts_handler_router

router = Router(name="company_jobposts")
router.include_router(company_jobposts_handler_router)
