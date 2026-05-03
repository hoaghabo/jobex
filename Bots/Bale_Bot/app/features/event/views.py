# app/features/event/views.py

from __future__ import annotations

from typing import Any

from app.features.event.api import get_current_events, get_event_detail
from app.features.event.formatters import (
    format_event_detail_text,
    format_event_list_text,
    is_event_full,
)
from app.features.event.keyboards import (
    get_event_detail_keyboard,
    get_events_list_keyboard,
)
from app.features.event.normalizers import (
    extract_event_detail,
    extract_events_list,
)
from app.features.event.urls import get_event_cover_url


async def build_events_list_view() -> tuple[str, Any]:
    response = await get_current_events()
    events = extract_events_list(response)

    text = format_event_list_text(events)
    keyboard = get_events_list_keyboard(events)

    return text, keyboard


async def build_event_detail_view(
    event_id: int | str,
    bale_user_id: int | str,
) -> tuple[str, Any, str | None]:
    response = await get_event_detail(
        event_id=event_id,
        bale_user_id=bale_user_id,
    )

    event = extract_event_detail(response)

    if not event:
        return "ایونت موردنظر پیدا نشد.", get_events_list_keyboard([]), None

    is_registered = bool(event.get("is_registered", False))
    registration_required = bool(event.get("is_registration_required", True))
    full = is_event_full(event)

    text = format_event_detail_text(
        event=event,
        is_registered=is_registered,
    )
    

    keyboard = get_event_detail_keyboard(
        event_id=event_id,
        is_registered=is_registered,
        is_full=full,
        registration_required=registration_required,
    )

    photo_url = event.get("cover_image")
    photo_file_id = event.get("cover_file_id")

    return text, keyboard, photo_url , photo_file_id
