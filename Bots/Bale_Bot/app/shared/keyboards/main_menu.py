from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="📅 ایونت‌های جاری"),
        ],
        [
            KeyboardButton(text="🎫 ایونت‌های ثبت‌نام‌شده من"),
            KeyboardButton(text="👤 پروفایل من"),
        ],
        [
            KeyboardButton(text="ℹ️ راهنما"),
        ],
    ]

    if is_admin:
        keyboard.extend([
            [
                KeyboardButton(text="🛠 مدیریت ایونت‌ها"),
                KeyboardButton(text="👥 لیست ثبت‌نامی‌ها"),
            ],
            [
                KeyboardButton(text="📊 آمار ایونت‌ها"),
                KeyboardButton(text="📁 خروجی اکسل"),
            ],
        ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید"
    )
