from aiogram.types import Message, CallbackQuery

from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.bot_user_api import get_user_status
from app.features.auth.permissions import is_admin_user, is_registered_user


client = BackendClient()


def get_bale_id_from_message(message: Message) -> str:
    user = message.from_user

    if not user or not user.id:
        raise ValueError("Cannot extract bale_id from message")

    return str(user.id)


def get_bale_id_from_callback(callback: CallbackQuery) -> str:
    user = callback.from_user

    if not user or not user.id:
        raise ValueError("Cannot extract bale_id from callback")

    return str(user.id)


async def get_status_from_message(message: Message) -> dict:
    result = await get_user_status(message)
    print("RAW USER STATUS FROM MESSAGE =>", result)
    return result


def is_admin_profile(status_response: dict) -> bool:
    print("CHECK STATUS RESPONSE =>", status_response)
    print("REGISTERED? =>", is_registered_user(status_response))
    print("ADMIN? =>", is_admin_user(status_response))

    return (
        is_registered_user(status_response)
        and is_admin_user(status_response)
    )


async def get_admin_status_from_message(message: Message):
    status_response = await get_status_from_message(message)

    if not is_admin_profile(status_response):
        return None

    return status_response


async def get_admin_events(bale_id: str):
    return await client.get(
        "api/bot/admin/events/",
        params={"bale_id": str(bale_id)},
    )


async def get_event_registrations_excel(event_id: int, bale_id: str):
    return await client.get_raw(
        f"api/bot/admin/events/{event_id}/registrations/export/",
        params={"bale_id": str(bale_id)},
    )
