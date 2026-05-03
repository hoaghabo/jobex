from aiogram.types import Message

from app.config import settings
from app.infrastructure.backend.client import BackendClient

client = BackendClient()


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def extract_user_payload(message: Message) -> dict:
    return {
        "bale_user_id": message.from_user.id if message.from_user else None,
        "chat_id": message.chat.id if message.chat else None,
        "first_name": message.from_user.first_name if message.from_user else None,
        "last_name": message.from_user.last_name if message.from_user else None,
        "username": message.from_user.username if message.from_user else None,
    }


async def register_or_update_user(
    message: Message,
    registered_full_name: str,
    phone_number: str,
) -> dict:
    payload = extract_user_payload(message)
    payload.update({
        "registered_full_name": registered_full_name,
        "phone_number": phone_number,
    })

    return await client.post(
        settings.BOT_USER_ENTRY_ENDPOINT,
        json=payload,
        headers=_build_bot_headers(),
    )


async def get_user_status(message: Message) -> dict:
    payload = extract_user_payload(message)

    return await client.post(
        settings.BOT_USER_STATUS_ENDPOINT,
        json=payload,
        headers=_build_bot_headers(),
    )
