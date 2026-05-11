from aiogram import Dispatcher

from app.features.auth.router import router as auth_router
from app.features.jobseeker_buy.router import router as jobseeker_router
from app.features.company_buy.router import router as company_router
from app.features.payment.router import router as payment_router




def setup_routers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(jobseeker_router)
    dp.include_router(company_router)
    dp.include_router(payment_router)

