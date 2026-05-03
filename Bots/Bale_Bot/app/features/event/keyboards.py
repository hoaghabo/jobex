# app/features/event/keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_events_list_keyboard(events: list[dict]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []

    for event in events:
        event_id = event.get("id")
        title = event.get("title") or "بدون عنوان"

        if not event_id:
            continue

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📌 {title}",
                    callback_data=f"event:detail:{event_id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔄 بروزرسانی",
                callback_data="event:list",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_event_detail_keyboard(
    event_id: int | str,
    is_registered: bool = False,
    is_full: bool = False,
    registration_required: bool = True,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if not registration_required:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="ℹ️ این ایونت نیاز به ثبت‌نام ندارد",
                    callback_data="event:noop",
                )
            ]
        )
    elif is_registered:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ ثبت‌نام شده",
                    callback_data="event:noop",
                )
            ]
        )
    elif is_full:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="ظرفیت تکمیل است",
                    callback_data="event:noop",
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📝 ثبت‌نام در این ایونت",
                    callback_data=f"event:register:{event_id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="🔙 بازگشت به لیست ایونت‌ها",
                callback_data="event:list",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def event_payment_confirm_keyboard(event_id: int | str) -> InlineKeyboardMarkup:
    """
    کیبورد تایید ادامه پرداخت برای ایونت پولی.

    اینجا هنوز لینک زرین‌پال نداریم.
    با کلیک روی ادامه پرداخت، بات از بک‌اند payment_url می‌گیرد.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ بله، ساخت لینک پرداخت",
                    callback_data=f"event:payment_confirm:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ خیر، انصراف",
                    callback_data=f"event:payment_cancel:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 مشاهده جزئیات ایونت",
                    callback_data=f"event:detail:{event_id}",
                )
            ],
        ]
    )


def event_after_payment_keyboard(
    event_id: int | str,
    payment_url: str,
) -> InlineKeyboardMarkup:
    """
    کیبورد بعد از ساخت لینک پرداخت زرین‌پال.

    در flow زرین‌پال، پرداخت داخل بات انجام نمی‌شود.
    کاربر با دکمه URL وارد درگاه می‌شود.
    callback زرین‌پال به بک‌اند می‌رود و بک‌اند پرداخت را verify می‌کند.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 پرداخت از طریق زرین‌پال",
                    url=payment_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 بررسی وضعیت ثبت‌نام",
                    callback_data=f"event:payment_check:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 مشاهده جزئیات ایونت",
                    callback_data=f"event:detail:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به لیست ایونت‌ها",
                    callback_data="event:list",
                )
            ],
        ]
    )


def back_to_event_detail_keyboard(event_id: int | str) -> InlineKeyboardMarkup:
    """
    کیبورد بازگشت به جزئیات ایونت.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 بازگشت به جزئیات ایونت",
                    callback_data=f"event:detail:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به لیست ایونت‌ها",
                    callback_data="event:list",
                )
            ],
        ]
    )


def event_registered_keyboard(event_id: int | str) -> InlineKeyboardMarkup:
    """
    کیبورد بعد از ثبت‌نام موفق.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📌 ایونت‌های من",
                    callback_data="events:my",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 مشاهده جزئیات ایونت",
                    callback_data=f"event:detail:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به لیست ایونت‌ها",
                    callback_data="event:list",
                )
            ],
        ]
    )


def event_payment_failed_keyboard(event_id: int | str) -> InlineKeyboardMarkup:
    """
    کیبورد در صورت خطا یا ناموفق بودن ساخت لینک پرداخت.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔁 تلاش مجدد برای ساخت لینک پرداخت",
                    callback_data=f"event:payment_confirm:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 مشاهده جزئیات ایونت",
                    callback_data=f"event:detail:{event_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به لیست ایونت‌ها",
                    callback_data="event:list",
                )
            ],
        ]
    )
