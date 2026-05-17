from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .api import get_my_company_list


async def build_choices_inline_keyboard(
    chat_id: int,
    choice_group_name: str,
    callback_prefix: str | None = None,
    row_width: int = 2,
    value_field: str = "value",
    label_field: str = "label",
    back_callback_data: str = "back_my_company_list_menu",
) -> tuple[InlineKeyboardMarkup, int]:
    """
    کیبورد اینلاین لیست انتخاب‌ها را از لیست شرکت‌های کاربر می‌سازد.

    Returns:
        tuple[InlineKeyboardMarkup, int]:
            - keyboard
            - تعداد دکمه‌های واقعی ساخته‌شده
    Raises:
        Exception:
            اگر دریافت لیست شرکت‌ها از بک‌اند با خطا مواجه شود.
    """

    if callback_prefix is None:
        callback_prefix = choice_group_name

    if not isinstance(row_width, int) or row_width < 1:
        row_width = 1

    response = await get_my_company_list(chat_id)
    print(f"====================> items {response}")

    if not isinstance(response, dict):
        response = {}

    items = response.get("results", [])
    if not isinstance(items, list):
        items = []

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
                callback_data=f"{callback_prefix}:{value}"
            )
        )

    keyboard_rows = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    keyboard_rows.append([
        InlineKeyboardButton(
            text="بازگشت",
            callback_data=back_callback_data
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    return keyboard, len(buttons)




async def get_my_company_list_inline_keyboard(chat_id: int) -> tuple[InlineKeyboardMarkup, int]:
    return await build_choices_inline_keyboard(
        chat_id=chat_id,
        choice_group_name="company_list",
        callback_prefix="company_list",
        row_width=1,
        value_field="id",
        label_field="company_name",
    )



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_company_edit_keyboard(company_id: int) -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(
                text="🏢 ویرایش نام شرکت",
                callback_data=f"edit_company:name:{company_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 نقش",
                callback_data=f"edit_company:role:{company_id}"
            ),
            InlineKeyboardButton(
                text="👥 اندازه سازمان",
                callback_data=f"edit_company:size:{company_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏭 صنعت",
                callback_data=f"edit_company:industry:{company_id}"
            ),
            InlineKeyboardButton(
                text="📍 شهر",
                callback_data=f"edit_company:city:{company_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📌 آدرس",
                callback_data=f"edit_company:address:{company_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="☎️ تلفن",
                callback_data=f"edit_company:phone:{company_id}"
            ),
            InlineKeyboardButton(
                text="🌐 وبسایت",
                callback_data=f"edit_company:website:{company_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="back_my_company_list"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def build_back_button(callback_data: str, text: str = "⬅️ بازگشت") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        ]
    )
    return keyboard