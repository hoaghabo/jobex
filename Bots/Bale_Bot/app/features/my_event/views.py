from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.shared.formatters.persian_number import fa_digits, format_jalali_date_fa
from .api import get_my_registered_events


def build_my_events_text(items: list[dict]) -> str:
    if not items:
        return "شما هنوز در هیچ ایونتی ثبت‌نام نکرده‌اید."

    lines = ["🎫 *ایونت‌های ثبت‌نام‌شده شما:*\n"]

    for index, item in enumerate(items, start=1):
        
        title = item.get("title") or "-"
        start_date = item.get("start_date") or "-"
        location = item.get("location") or "-"
        event_id = item.get("event_id") or "-"
        Facilitator_name = item.get("facilitator_name")

        lines.append(
            f"*{index}) {title}*\n"
            f"  تسهیلگر‌: {Facilitator_name}\n"
            f"🕒 زمان شروع: {format_jalali_date_fa(start_date)}\n"
            f"📍 مکان: {location}\n"
            f"🆔 شناسه ایونت: {fa_digits(event_id)}\n"
        )

    return "\n".join(lines)


def build_my_events_keyboard(items: list[dict]) -> InlineKeyboardMarkup | None:
    if not items:
        return None

    builder = InlineKeyboardBuilder()

    for item in items:
        event_id = item.get("event_id")
        title = item.get("title") or "مشاهده ایونت"

        if not event_id:
            continue

        builder.button(
            text=f"🎫 {title}",
            callback_data=f"event:detail:my:{event_id}",
        )

    builder.adjust(1)
    return builder.as_markup()


async def build_my_events_view(
    bale_user_id: int,
) -> tuple[str, InlineKeyboardMarkup | None]:
    data = await get_my_registered_events(bale_user_id=bale_user_id)
    items = data.get("results", [])

    text = build_my_events_text(items)
    keyboard = build_my_events_keyboard(items)

    return text, keyboard
