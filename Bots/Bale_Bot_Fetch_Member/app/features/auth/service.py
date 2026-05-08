from aiogram.types import Message

from app.infrastructure.backend.client import BackendAPIError
from app.infrastructure.backend.bot_user_api import (
    get_user_status,
    register_or_update_user,
)


class UserAccessResult:
    def __init__(
        self,
        *,
        ok: bool,
        is_blocked: bool = False,
        is_registered: bool = False,
        is_admin: bool = False,
        state: str | None = None,
        state_data: dict | None = None,
        created: bool = False,
        raw_data: dict | None = None,
        error: str | None = None,
    ):
        self.ok = ok
        self.is_blocked = is_blocked
        self.is_registered = is_registered
        self.is_admin = is_admin
        self.state = state
        self.state_data = state_data or {}
        self.created = created
        self.raw_data = raw_data or {}
        self.error = error


async def ensure_user_exists(message: Message) -> UserAccessResult:
    try:
        response = await register_or_update_user(message)

        if not response.get("ok"):
            return UserAccessResult(
                ok=False,
                error="Backend response is not ok",
                raw_data=response,
            )

        user_data = response.get("user", {})

        return UserAccessResult(
            ok=True,
            is_blocked=user_data.get("is_blocked", False),
            is_registered=user_data.get("is_registered", False),
            state=user_data.get("state"),
            created=response.get("created", False),
            raw_data=response,
        )

    except BackendAPIError as e:
        return UserAccessResult(ok=False, error=str(e))


async def fetch_user_status(message: Message) -> UserAccessResult:
    try:
        response = await get_user_status(message)

        if not response.get("ok"):
            return UserAccessResult(
                ok=False,
                error="Backend response is not ok",
                raw_data=response,
            )

        user_data = response.get("user", {})

        return UserAccessResult(
            ok=True,
            is_blocked=user_data.get("is_blocked", False),
            is_registered=user_data.get("is_registered", False),
            is_admin=user_data.get("is_admin", False),
            state=user_data.get("state"),
            state_data=user_data.get("state_data", {}),
            created=response.get("created", False),
            raw_data=response,
        )

    except BackendAPIError as e:
        return UserAccessResult(ok=False, error=str(e))


async def check_user_access(message: Message) -> UserAccessResult:
    """
    ورودی کاربر را ثبت/آپدیت می‌کند و سپس وضعیت او را برای ادامه کار برمی‌گرداند.
    """
    register_result = await ensure_user_exists(message)
    if not register_result.ok:
        return register_result

    status_result = await fetch_user_status(message)
    if not status_result.ok:
        return status_result

    return status_result
