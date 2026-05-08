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


async def get_organization_size_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="organization_size",
        callback_prefix="organization_size",
        row_width=2,
    )


async def get_city_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="city",
        callback_prefix="city",
        row_width=2,
    )


