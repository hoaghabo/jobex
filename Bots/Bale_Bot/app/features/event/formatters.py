# app/features/event/formatters.py

from __future__ import annotations

from typing import Any

from app.shared.formatters.persian_number import fa_digits


def is_event_full(event: dict[str, Any]) -> bool:
    if "is_full" in event:
        return bool(event.get("is_full"))

    remaining_capacity = event.get("remaining_capacity")

    if remaining_capacity is not None:
        try:
            return int(fa_digits(remaining_capacity)) <= 0
        except (TypeError, ValueError):
            pass

    capacity = event.get("capacity")
    registrations_count = event.get("registrations_count")

    try:
        if capacity is not None and registrations_count is not None:
            return int(registrations_count) >= int(capacity)
    except (TypeError, ValueError):
        pass

    return False


def format_price(event: dict[str, Any]) -> str:
    if event.get("is_free") is True:
        return "رایگان"

    price = event.get("price")

    if price in (None, "", 0, "0", "0.00"):
        return "رایگان"

    return f"{fa_digits(price)} تومان"


def format_capacity(event: dict[str, Any]) -> str:
    if event.get("capacity") in (None, ""):
        return "نامحدود"

    remaining = event.get("remaining_capacity")

    if remaining is not None:
        return f"{fa_digits(remaining)} ظرفیت باقی‌مانده"

    capacity = event.get("capacity")
    registrations_count = event.get("registrations_count")

    if registrations_count is not None:
        return f"{registrations_count} / {capacity}"

    return str(capacity)


def format_schedule(event: dict[str, Any]) -> str:
    schedule = event.get("schedule_summary")

    if schedule:
        return fa_digits(schedule)

    start_date = event.get("start_date")
    end_date = event.get("end_date")

    if start_date and end_date:
        return f"{fa_digits(start_date)} تا {fa_digits(end_date)}"

    if start_date:
        return fa_digits(start_date)

    return "نامشخص"



def format_event_list_text(events: list[dict[str, Any]]) -> str:
    if not events:
        return "در حال حاضر ایونتی برای نمایش وجود ندارد."

    lines = ["📅 *لیست ایونت‌ها*\n"]

    for event in events:
        title = event.get("title") or "بدون عنوان"
        event_type = event.get("event_type") or "-"
        price = format_price(event)
        schedule = format_schedule(event)
        Facilitator_name = event.get("facilitator_name")

        print(f"EVENT TEXT==============> {schedule}")

        lines.append(
            f"• *{title}*\n"
            f"  تسهیلگر‌: {Facilitator_name}\n"
            f"  نوع: {event_type}\n"
            f"  زمان: {schedule}\n"
            f"  قیمت: {price}\n"
        )

    lines.append("برای مشاهده جزئیات، یکی از ایونت‌ها را انتخاب کنید.")

    return "\n".join(lines)


def format_event_detail_text(
    event: dict[str, Any],
    *,
    is_registered: bool,
) -> str:
    title = event.get("title") or "بدون عنوان"
    description = event.get("description") or "توضیحاتی ثبت نشده است."
    event_type = event.get("event_type") or "-"
    schedule = format_schedule(event)
    price = format_price(event)
    capacity = format_capacity(event)

    status_text = (
        "✅ شما در این ایونت ثبت‌نام کرده‌اید."
        if is_registered
        else "❌ هنوز در این ایونت ثبت‌نام نکرده‌اید."
    )

    lines = [
        f"🎟 *{title}*",
        "",
        f"🗂 نوع: {event_type}",
        f"🕒 زمان: {schedule}",
        f"💰 قیمت: {price}",
        f"👥 ظرفیت: {capacity}",
        "",
        "📝 توضیحات:",
        str(description),
        "",
        status_text,
    ]

    return "\n".join(lines)


def trim_caption(text: str, max_length: int = 900) -> str:
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
