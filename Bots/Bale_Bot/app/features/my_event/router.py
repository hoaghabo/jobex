from aiogram import Router, F

from .handler import my_events_message_handler, my_events_callback_handler

router = Router()

router.message(F.text == "🎫 ایونت‌های ثبت‌نام‌شده من")(my_events_message_handler)
router.callback_query(F.data == "events:my")(my_events_callback_handler)
