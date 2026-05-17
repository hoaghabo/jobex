from aiogram import Router
from app.features.jobseeker.update_resume.handlers import router as update_resume_handlers_router
from app.features.jobseeker.upload_resume.handlers import router as upload_resume_handlers_router
from app.features.jobseeker.jobseeker_main.handlers import router as jobseeker_main_handlers_router
from app.features.jobseeker.ask_new_campaign.handlers import router as  jobseeker_ask_new_campain
from app.features.jobseeker.my_campaigns_list.handlers import router as  jobseeker_my_campain_list

router = Router(name="jobseeker")
router.include_router(update_resume_handlers_router)
router.include_router(upload_resume_handlers_router)
router.include_router(jobseeker_main_handlers_router)
router.include_router(jobseeker_ask_new_campain)
router.include_router(jobseeker_my_campain_list)
