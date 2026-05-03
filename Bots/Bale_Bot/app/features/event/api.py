# app/features/event/api.py

from typing import Any
from urllib.parse import urlencode

from app.infrastructure.backend.client import BackendClient


client = BackendClient()


def _make_query_params(params: dict[str, Any]) -> str:
    cleaned_params = {
        key: value
        for key, value in params.items()
        if value is not None
    }

    if not cleaned_params:
        return ""

    return "?" + urlencode(cleaned_params)


async def get_current_events() -> Any:
    """
    دریافت لیست ایونت‌های فعال/جاری.
    """
    return await client.get("/api/events/")


async def get_event_detail(
    event_id: int | str,
    bale_user_id: int | str | None = None,
) -> dict[str, Any]:
    """
    دریافت جزئیات یک ایونت.
    """
    query = _make_query_params(
        {
            "bale_user_id": bale_user_id,
        }
    )

    return await client.get(f"/api/events/{event_id}/{query}")


async def get_event_registration_status(
    event_id: int | str,
    bale_user_id: int | str,
) -> dict[str, Any]:
    """
    وضعیت ثبت‌نام کاربر در ایونت.
    """
    query = _make_query_params(
        {
            "bale_user_id": bale_user_id,
        }
    )

    return await client.get(
        f"/api/events/{event_id}/registration-status/{query}"
    )


async def register_user_in_event(
    event_id: int | str,
    bale_user_id: int | str,
) -> dict[str, Any]:
    """
    ثبت‌نام مستقیم در ایونت (فقط ایونت رایگان).
    """
    payload = {
        "bale_user_id": bale_user_id,
    }

    return await client.post(
        f"/api/events/{event_id}/register/",
        json=payload,
    )


async def get_my_events(
    bale_user_id: int | str,
) -> Any:
    """
    ایونت‌های ثبت‌نام‌شده کاربر.
    """
    query = _make_query_params(
        {
            "bale_user_id": bale_user_id,
        }
    )

    return await client.get(f"/api/bot/my-events/{query}")


async def create_event_payment(
    event_id: int | str,
    bale_user_id: int | str,
    bale_chat_id: int | str | None = None,
    bale_payment_message_id: int | str | None = None,
) -> dict[str, Any]:
    payload = {
        "bale_user_id": bale_user_id,
        "bale_chat_id": bale_chat_id,
        "bale_payment_message_id": bale_payment_message_id,
    }

    payload = {
        key: value
        for key, value in payload.items()
        if value is not None
    }

    print(f"create_event_payment payload ====================> {payload}")

    return await client.post(
        f"/api/bot/events/{event_id}/create-payment/",
        json=payload,
    )
