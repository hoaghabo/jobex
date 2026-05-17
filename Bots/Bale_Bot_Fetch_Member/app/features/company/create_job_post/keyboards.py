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


async def get_degree_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="degree",
        callback_prefix="jobpost_degree",
        row_width=2,
    )


async def get_job_title_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="job_title",
        callback_prefix="job_title",
        row_width=2,
    )


async def get_cooperation_type_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="cooperation_type",
        callback_prefix="cooperation_type",
        row_width=2,
    )


async def get_attendance_type_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="attendance_type",
        callback_prefix="attendance_type",
        row_width=2,
    )


async def get_minimum_work_experiencee_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="minimum_work_experience",
        callback_prefix="minimum_work_experience",
        row_width=2,
    )


async def get_working_days_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="working_days",
        callback_prefix="working_days",
        row_width=2,
    )


async def get_overtime_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="دارد", callback_data="has_over_time:True"),
                InlineKeyboardButton(text="ندارد", callback_data="has_over_time:False"),
            ]
        ]
    )


async def get_working_hours_inline_keyboard() -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        choice_group_name="working_hours",
        callback_prefix="working_hours",
        row_width=2,
    )


async def get_salary_type_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="توافقی",
                    callback_data="salary:negotiable"
                ),
                InlineKeyboardButton(
                    text="مقدار مشخص",
                    callback_data="salary:fixed"
                ),
            ]
        ]
    )




def build_choices_inline_keyboard_from_items(
    items: list[dict],
    choice_group_name: str,
    callback_prefix: str | None = None,
    row_width: int = 2,
    value_field: str = "value",
    label_field: str = "label",
    back_callback_data: str | None = None,
) -> tuple[InlineKeyboardMarkup, int]:

    if callback_prefix is None:
        callback_prefix = choice_group_name

    if not isinstance(items, list):
        items = []

    if not isinstance(row_width, int) or row_width < 1:
        row_width = 1

    buttons: list[InlineKeyboardButton] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        value = item.get(value_field)
        label = item.get(label_field)

        if value is None or label in (None, ""):
            continue

        buttons.append(
            InlineKeyboardButton(
                text=str(label),
                callback_data=f"{callback_prefix}:{value}",
            )
        )

    keyboard_rows = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    if back_callback_data:
        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text="بازگشت",
                    callback_data=back_callback_data,
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows), len(buttons)
