from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_jobseeker_main_menu():
    keyboard = [
        [
            KeyboardButton(text="آپلود فایل رزومه"),
            KeyboardButton(text="بروزرسانی رزومه"),
        ],
        [
            KeyboardButton(text="لیست کمپین های من"),
            KeyboardButton(text="درخواست کمپین جدید"),
        ],
        [KeyboardButton(text = "بازگشت به منو اصلی")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
