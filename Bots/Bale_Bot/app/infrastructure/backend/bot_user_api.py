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
        "user_id": user_id,
    })

    return await client.post(
        settings.BOT_USER_ENTRY_ENDPOINT,
        json=payload,
        headers=_build_bot_headers(),
    )

async def get_user_status(message: Message) -> dict:
    chat_id = message.from_user.id if message.from_user else None

    try:
        return await client.get(
            f"{settings.BOT_USER_STATUS_ENDPOINT}?chat_id={chat_id}",
            headers=_build_bot_headers(),
        )
    except BackendAPIError as e:
        status_code = getattr(e, "status_code", None)

        if status_code in (403, 404):
            return {
                "registered": False,
                "detail": "کاربر پیدا نشد."
            }

        raise
    
    

def normalize_phone_number(phone_number: str | None) -> str | None:
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

    if phone_number.startswith("09") and len(phone_number) == 11:
        return "98" + phone_number[1:]

    if phone_number.startswith("9") and len(phone_number) == 10:
        return "98" + phone_number

    if phone_number.startswith("98") and len(phone_number) == 12:
        return phone_number

    return phone_number


def extract_phone_number_from_status(status_response: dict | None) -> str | None:
    """
    شماره موبایل را از responseهای مختلف بک‌اند استخراج و نرمال‌سازی می‌کند.
    """

    if not isinstance(status_response, dict):
        return None

    # حالت مستقیم
    phone_number = status_response.get("phone_number")
    if phone_number:
        return normalize_phone_number(phone_number)

    # account فقط اگر dict باشد
    account = status_response.get("account")
    if isinstance(account, dict):
        phone_number = account.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

    # user فقط اگر dict باشد
    user = status_response.get("user")
    if isinstance(user, dict):
        phone_number = user.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

    # data فقط اگر dict باشد
    data = status_response.get("data")
    if isinstance(data, dict):
        phone_number = data.get("phone_number")
        if phone_number:
            return normalize_phone_number(phone_number)

        data_account = data.get("account")
        if isinstance(data_account, dict):
            phone_number = data_account.get("phone_number")
            if phone_number:
                return normalize_phone_number(phone_number)

    return None


async def create_jobseeker_profile(message: Message) -> dict:
    status_response = await get_user_status(message)

    if not isinstance(status_response, dict):
        raise BackendAPIError(
            message=f"خروجی get_user_status نامعتبر است: {status_response}",
            status_code=400,
        )
    print("status_response:", status_response, type(status_response))
    phone_number = extract_phone_number_from_status(status_response)
    print(f'===============================> {phone_number}')

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
    status_response = await get_user_status(message)

    if not isinstance(status_response, dict):
        raise BackendAPIError(
            message=f"خروجی get_user_status نامعتبر است: {status_response}",
            status_code=400,
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
