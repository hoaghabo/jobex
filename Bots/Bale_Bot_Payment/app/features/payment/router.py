from aiogram import Router
from app.features.payment.handlers import router  as payment_router
 
router = Router(name="payment")
router.include_router(payment_router)
