
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .api import get_company_jobpost_list_by_company










async def build_choices_inline_keyboard(
    chat_id: int,
    company_id: int,
    choice_group_name: str,
    callback_prefix: str | None = None,
    row_width: int = 2,
    value_field: str = "value",
    label_field: str = "label",
) -> InlineKeyboardMarkup:

    response = await get_company_jobpost_list_by_company(chat_id=chat_id , company_id=company_id)
    print(f"====================> items {response}")

    items = response.get("results", [])

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
            callback_data=f"back_my_company_job_post_to_company_list_menu:{company_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




async def get_my_company_Job_list_inline_keyboard(chat_id , company_id) -> InlineKeyboardMarkup:
    return await build_choices_inline_keyboard(
        chat_id = chat_id,
        company_id = company_id,
        choice_group_name="job_post_list",
        callback_prefix="job_post_list",
        row_width=1,
        value_field="id",
        label_field="job_title",
    )

def build_back_button(callback_data: str, text: str = "⬅️ بازگشت") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        ]
    )
    return keyboard




def build_jobpost_detail_keyboard(
    chat_id: int,
    company_id: int,
    jobpost_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 حذف آگهی",
                    callback_data=f"delete_jobpost:{chat_id}:{company_id}:{jobpost_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 برگشت",
                    callback_data=f"back_to_jobpost_list:{company_id}",
                )
            ],
        ]
    )





def build_empty_company_list_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ ثبت شرکت جدید",
                    callback_data="create_company_From_my_company_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="back_to_main_menu"
                )
            ]
        ]
    )
