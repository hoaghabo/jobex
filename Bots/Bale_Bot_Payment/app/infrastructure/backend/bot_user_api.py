from aiogram.types import Message

from app.config import settings
from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError

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
    user_id: int,
) -> dict:
    payload = extract_user_payload(message)
    payload.update({
        "registered_full_name": registered_full_name,
        "phone_number": phone_number,
        "bale_bot_name": "fetch_member",
        "user_id": user_id,
    })

    return await client.post(
        settings.BOT_USER_ENTRY_ENDPOINT,
        json=payload,
        headers=_build_bot_headers(),
    )


async def get_user_status(message: Message) -> dict | None:
    """دریافت وضعیت کاربر از بک‌اند بر اساس Message"""
    if not message or not message.from_user:
        return None
    
    chat_id = message.from_user.id

    try:
        response = await client.get(
            f"{settings.BOT_USER_STATUS_ENDPOINT}?chat_id={chat_id}",
            headers=_build_bot_headers(),
        )
        return response
    except BackendAPIError as e:
        status_code = getattr(e, "status_code", None)

        if status_code in (403, 404):
            return {
                "is_registered": False,
                "is_bot_bale_member": False,
                "detail": "کاربر پیدا نشد."
            }

        # برای خطاهای دیگر، None برمی‌گردانیم
        return None


async def get_user_status_by_chat_id(chat_id: int | str | None) -> dict | None:
    """دریافت وضعیت کاربر از بک‌اند بر اساس chat_id"""
    if not chat_id:
        return {
            "is_registered": False,
            "is_bot_bale_member": False,
            "detail": "chat_id نامعتبر است."
        }

    try:
        response = await client.get(
            f"{settings.BOT_USER_STATUS_ENDPOINT}?chat_id={chat_id}",
            headers=_build_bot_headers(),
        )
        return response
    except BackendAPIError as e:
        status_code = getattr(e, "status_code", None)

        if status_code in (403, 404):
            return {
                "is_registered": False,
                "is_bot_bale_member": False,
                "detail": "کاربر پیدا نشد."
            }

        # برای خطاهای دیگر، None برمی‌گردانیم
        return None


def normalize_phone_number(phone_number: str | None) -> str | None:
    """نرمال‌سازی شماره تلفن به فرمت 98XXXXXXXXX"""
    if not phone_number:
        return None

    phone_number = str(phone_number).strip()
    phone_number = (
        phone_number
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    # 09XXXXXXXXX -> 98XXXXXXXXX
    if phone_number.startswith("09") and len(phone_number) == 11:
        return "98" + phone_number[1:]

    # 9XXXXXXXXX -> 98XXXXXXXXX
    if phone_number.startswith("9") and len(phone_number) == 10:
        return "98" + phone_number

    # 98XXXXXXXXX (قبلاً نرمال است)
    if phone_number.startswith("98") and len(phone_number) == 12:
        return phone_number

    # فرمت نامعتبر
    return phone_number


def extract_phone_number_from_status(status_response: dict | None) -> str | None:
    """استخراج و نرمال‌سازی شماره موبایل از پاسخ بک‌اند"""
    if not isinstance(status_response, dict):
        return None

    # جستجو در سطح اول
    phone_number = status_response.get("phone_number")
    if phone_number:
        return normalize_phone_number(phone_number)

    # جستجو در account
    account = status_response.get("account")
    if isinstance(account, dict):
        phone_number = account.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

    # جستجو در user
    user = status_response.get("user")
    if isinstance(user, dict):
        phone_number = user.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

    # جستجو در data
    data = status_response.get("data")
    if isinstance(data, dict):
        phone_number = data.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

        # جستجو در data.account
        data_account = data.get("account")
        if isinstance(data_account, dict):
            phone_number = data_account.get("phone_number")
            if phone_number:
                return normalize_phone_number(phone_number)

    return None


async def create_jobseeker_profile(message: Message) -> dict:
    """ایجاد پروفایل کارجو"""
    status_response = await get_user_status(message)

    if not status_response:
        raise BackendAPIError(
            message="دریافت وضعیت کاربر از بک‌اند با خطا مواجه شد.",
            status_code=500,
        )

    phone_number = extract_phone_number_from_status(status_response)

    if not phone_number:
        raise BackendAPIError(
            message="شماره موبایل کاربر از بک‌اند دریافت نشد.",
            status_code=400,
        )

    return await client.post(
        "api/crm/customer/jobseeker/profile/",
        json={"phone_number": phone_number},
        headers=_build_bot_headers(),
    )


async def create_company_profile(message: Message) -> dict:
    """ایجاد پروفایل شرکت"""
    status_response = await get_user_status(message)

    if not status_response:
        raise BackendAPIError(
            message="دریافت وضعیت کاربر از بک‌اند با خطا مواجه شد.",
            status_code=500,
        )

    phone_number = extract_phone_number_from_status(status_response)

    if not phone_number:
        raise BackendAPIError(
            message="شماره موبایل کاربر از بک‌اند دریافت نشد.",
            status_code=400,
        )

    return await client.post(
        "api/crm/customer/company/profile/",
        json={"phone_number": phone_number},
        headers=_build_bot_headers(),
    )
