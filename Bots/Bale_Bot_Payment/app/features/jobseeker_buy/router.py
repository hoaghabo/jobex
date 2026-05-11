from aiogram import Router
from app.features.jobseeker_buy.buy_package.handlers import router as jobseeker_buypackage_handlers_router

router = Router(name="jobseeker")
router.include_router(jobseeker_buypackage_handlers_router)
