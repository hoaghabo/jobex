# app/features/auth/permissions.py

from aiogram.types import Message

from app.infrastructure.backend.bot_user_api import get_user_status


def is_admin_user(backend_response: dict | None) -> bool:
    """
    تشخیص اینکه کاربر مدیر هست یا نه
    بر اساس پاسخ بک‌اند.
    """

    if not backend_response:
        return False

    if backend_response.get("is_admin") is True:
        return True

    if backend_response.get("role") == "admin":
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("is_admin") is True:
            return True

        if user_data.get("role") == "admin":
            return True

    return False


def is_registered_user(backend_response: dict | None) -> bool:
    """
    تشخیص اینکه کاربر ثبت‌نام کرده یا نه.
    """

    if not backend_response:
        return False

    if backend_response.get("is_registered") is True:
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("is_registered") is True:
            return True

    return False


async def check_user_is_admin(message: Message) -> bool:
    """
    هرجا لازم بود دسترسی مدیر را واقعی و امن چک کنیم،
    از بک‌اند وضعیت کاربر را می‌گیریم.
    """

    status_response = await get_user_status(message)
    return is_admin_user(status_response)


async def check_user_is_registered(message: Message) -> bool:
    """
    چک ثبت‌نام بودن کاربر از بک‌اند.
    """

    status_response = await get_user_status(message)
    return is_registered_user(status_response)
