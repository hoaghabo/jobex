from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_company_main_menu():
    keyboard = [
        [
            KeyboardButton(text="آگهی شغلی های من"),
            KeyboardButton(text="درخواست آگهی شغلی"),
        ],
        [
            KeyboardButton(text="شرکت های من"),
            KeyboardButton(text="ثبت شرکت جدید"),
        ],
        [KeyboardButton(text = "بازگشت به منو اصلی")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
