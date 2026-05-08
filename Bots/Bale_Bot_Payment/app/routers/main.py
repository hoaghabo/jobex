from aiogram import Dispatcher

from app.features.auth.router import router as auth_router
from app.features.jobseeker.router import router as jobseeker_router
from app.features.company.router import router as company_router




def setup_routers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(jobseeker_router)
    dp.include_router(company_router)

