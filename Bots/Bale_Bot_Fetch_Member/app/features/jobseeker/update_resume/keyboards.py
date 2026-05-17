from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .api import get_choices_items




async def build_choices_inline_keyboard(
    choice_group_name: str,
    callback_prefix: str | None = None,
    row_width: int = 2,
) -> InlineKeyboardMarkup:
    items = await get_choices_items(choice_group_name)

    if callback_prefix is None:
        callback_prefix = choice_group_name

    buttons = []

    for item in items:
        value = item.get("value")
        label = item.get("label")

        if not value or not label:
            continue

        buttons.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"{callback_prefix}:{value}"
            )
        )

    keyboard = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    keyboard.append([
        InlineKeyboardButton(
            text="بازگشت",
            callback_data="back_update_resume_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)





##########################################################


async def get_degree_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="degree",
        callback_prefix="degree",
        row_width=2,
    )



async def get_work_enthusiasts_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="work_enthusiasts",
        callback_prefix="work_enthusiasts",
        row_width=2,
    )


async def get_salary_range_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="salary_range",
        callback_prefix="salary_range",
        row_width=2,
    )


async def get_work_location_priority_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="work_location_priority",
        callback_prefix="work_location_priority",
        row_width=2,
    )







async def update_jobseeker_resume_keyboards():
    keyboard = [
        [
            InlineKeyboardButton(
                text="آپدیت مدرک تحصیلی",
                callback_data="update_degree"
            ),
        ],
        [
            InlineKeyboardButton(
                text="آپدیت علاقه‌مندی شغلی",
                callback_data="update_work_enthusiasts"
            ),
        ],
        [
            InlineKeyboardButton(
                text="آپدیت بازه حقوق درخواستی",
                callback_data="update_salary_range"
            ),
        ],
        [
            InlineKeyboardButton(
                text="آپدیت اولویت محل کار",
                callback_data="update_work_location_priority"
            ),
        ],
        [
            InlineKeyboardButton(
                text="بازگشت",
                callback_data="back_main_menu_jobseeker"
            )
        ]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
