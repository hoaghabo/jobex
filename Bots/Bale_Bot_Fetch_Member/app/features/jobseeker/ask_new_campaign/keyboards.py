from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .api import get_campaign_channels









async def build_choices_inline_keyboard(
    choice_group_name: str,
    callback_prefix: str | None = None,
    row_width: int = 2,
    value_field: str = "value",
    label_field: str = "label",
) -> InlineKeyboardMarkup:

    items = await get_campaign_channels()
    print(f"====================> items {items}")

    if callback_prefix is None:
        callback_prefix = choice_group_name

    buttons = []

    for item in items:
        value = item.get(value_field)
        label = item.get(label_field)

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
            callback_data="back_ask_camagin_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




async def get_campaign_request_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="campaign_request",
        callback_prefix="campaign_request",
        row_width=1,
        value_field="id",
        label_field="title",
    )
