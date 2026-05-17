from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .api import get_choices_items,get_role_membership_channels , get_city_list




async def build_choices_inline_keyboard(
    choice_group_name: str | None = None,
    callback_prefix: str | None = None,
    row_width: int = 2,
    value_field: str = "value",
    label_field: str = "label",
) -> InlineKeyboardMarkup:

    items = []

    if choice_group_name == "membership_role":
        items = await get_role_membership_channels()

    elif choice_group_name == "city":
        items = await get_city_list()
    
    elif choice_group_name:
        items = await get_choices_items(choice_group_name)
    
    if callback_prefix is None:
        callback_prefix = choice_group_name or "menu"

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

    keyboard = []

    if buttons:
        keyboard.extend(
            [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
        )

    keyboard.append([
        InlineKeyboardButton(
            text="بازگشت",
            callback_data=f"{callback_prefix}:back"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)







##########################################################


async def get_organization_size_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="organization_size",
        callback_prefix="organization_size",
        value_field="id",
        label_field="name",
        row_width=2,
    )


async def get_city_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="city",
        callback_prefix="city",
        value_field="id",
        label_field="name",
        row_width=2,
    )


async def get_membership_role_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="membership_role",
        callback_prefix="membership_role",
        row_width=1,
        value_field="id",
        label_field="name",
    )

