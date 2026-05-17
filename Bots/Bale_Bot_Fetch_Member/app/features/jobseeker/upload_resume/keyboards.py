from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="انصراف",
                callback_data="cancel_resume_upload"
            )
        ]
    ]
)

