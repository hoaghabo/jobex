from aiogram import Router
from app.features.company_buy.buy_package.handlers import router  as company_buy_package_router
 
router = Router(name="company")
router.include_router(company_buy_package_router)
