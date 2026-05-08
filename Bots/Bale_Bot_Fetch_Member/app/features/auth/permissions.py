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

    if backend_response.get("registered") is True:
        return True

    if backend_response.get("is_registered") is True:
        return True

    if backend_response.get("is_bot_bale_member") is True:
        return True

    # اگر کاربر admin باشد، معمولاً یعنی در سیستم شناخته شده است
    if backend_response.get("role") == "admin":
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("registered") is True:
            return True

        if user_data.get("is_registered") is True:
            return True

        if user_data.get("is_bot_bale_member") is True:
            return True

        if user_data.get("role") == "admin":
            return True

    return False


def is_jobseeker_member_user(backend_response: dict | None) -> bool:
    """
    تشخیص اینکه کاربر عضو بخش کارجویی هست یا نه.
    """

    if not backend_response:
        return False

    if backend_response.get("is_jobseeker_member") is True:
        return True

    if backend_response.get("jobseeker_member") is True:
        return True

    if backend_response.get("is_jobseeker") is True:
        return True

    if backend_response.get("role") in ("jobseeker", "job_seeker"):
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("is_jobseeker_member") is True:
            return True

        if user_data.get("jobseeker_member") is True:
            return True

        if user_data.get("is_jobseeker") is True:
            return True

        if user_data.get("role") in ("jobseeker", "job_seeker"):
            return True

    return False


def is_company_member_user(backend_response: dict | None) -> bool:
    """
    تشخیص اینکه کاربر عضو بخش کارفرمایی/شرکتی هست یا نه.
    """

    if not backend_response:
        return False

    if backend_response.get("is_company_member") is True:
        return True

    if backend_response.get("company_member") is True:
        return True

    if backend_response.get("is_company") is True:
        return True

    if backend_response.get("role") in ("company", "employer"):
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("is_company_member") is True:
            return True

        if user_data.get("company_member") is True:
            return True

        if user_data.get("is_company") is True:
            return True

        if user_data.get("role") in ("company", "employer"):
            return True

    return False


def extract_menu_flags(backend_response: dict | None) -> dict:
    """
    استخراج وضعیت‌های لازم برای ساخت منوی اصلی بات.

    تابع get_main_menu_keyboard این پارامترها را می‌گیرد:

    - is_jobseeker_member
    - is_company_member
    - is_bot_bale_member

    پس این تابع پاسخ بک‌اند را به همین فرمت تبدیل می‌کند.
    """

    return {
        "is_jobseeker_member": is_jobseeker_member_user(backend_response),
        "is_company_member": is_company_member_user(backend_response),
        "is_bot_bale_member": is_registered_user(backend_response),
    }


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


async def get_user_menu_flags(message: Message) -> dict:
    """
    دریافت وضعیت کاربر از بک‌اند و تبدیل آن به پارامترهای منوی اصلی.
    """

    status_response = await get_user_status(message)
    return extract_menu_flags(status_response)
