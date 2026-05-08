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

    return InlineKeyboardMarkup(inline_keyboard=keyboard)





##########################################################


async def get_degree_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="degree",
        callback_prefix="degree",
        row_width=2,
    )


async def get_city_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="city",
        callback_prefix="city",
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


async def get_campaign_request_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="campaign_request",
        callback_prefix="campaign_request",
        row_width=1,
    )



def to_persian_digits(number: int) -> str:
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return "".join(persian_digits[int(d)] for d in str(number))


async def get_birthday_day_inline_keyboard() -> InlineKeyboardMarkup:
    buttons = []

    for day in range(1, 32):
        buttons.append(
            InlineKeyboardButton(
                text=to_persian_digits(day),
                callback_data=f"birthday_day:{day}"
            )
        )

    row_width = 5

    keyboard = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_birthday_month_inline_keyboard() -> InlineKeyboardMarkup:
    months = [
        ("فروردین", 1),
        ("اردیبهشت", 2),
        ("خرداد", 3),
        ("تیر", 4),
        ("مرداد", 5),
        ("شهریور", 6),
        ("مهر", 7),
        ("آبان", 8),
        ("آذر", 9),
        ("دی", 10),
        ("بهمن", 11),
        ("اسفند", 12),
    ]

    buttons = [
        InlineKeyboardButton(
            text=month_name,
            callback_data=f"birthday_month:{month_number}"
        )
        for month_name, month_number in months
    ]

    row_width = 3
    keyboard = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)