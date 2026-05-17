from typing import Any, Dict, Optional

from app.config import settings
from app.infrastructure.backend.client import BackendClient

client = BackendClient()

COMPANY_JOBPOST_BASE_URL = "/api/crm/customer/company/jobpost"


def _build_bot_headers() -> Dict[str, str]:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def _validate_company_id(company_id: Optional[int]) -> None:
    if not company_id:
        raise ValueError("company_id is required")


def _validate_jobpost_id(jobpost_id: Optional[int]) -> None:
    if not jobpost_id:
        raise ValueError("jobpost_id is required")


async def get_company_jobpost_list_by_company(
    chat_id: int,
    company_id: int,
) -> Any:
    """
    دریافت لیست آگهی‌های شغلی یک شرکت مشخص.

    Backend:
        GET /api/crm/customer/company/jobpost/me/?chat_id=<chat_id>&company=<company_id>
    """
    _validate_company_id(company_id)

    return await client.get(
        f"{COMPANY_JOBPOST_BASE_URL}/me/",
        params={"chat_id": chat_id, "company": company_id},
        headers=_build_bot_headers(),
    )


async def get_company_jobpost_detail(
    chat_id: int,
    company_id: int,
    jobpost_id: int,
) -> Any:
    """
    دریافت جزئیات یک آگهی شغلی.

    Backend:
        GET /api/crm/customer/company/jobpost/<jobpost_id>/?chat_id=<chat_id>&company=<company_id>
    """
    _validate_company_id(company_id)
    _validate_jobpost_id(jobpost_id)

    return await client.get(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        params={"chat_id": chat_id, "company": company_id},
        headers=_build_bot_headers(),
    )


async def create_company_jobpost(
    chat_id: int,
    company_id: int,
    data: Dict[str, Any],
) -> Any:
    """
    ساخت آگهی شغلی جدید.

    Backend:
        POST /api/crm/customer/company/jobpost/me/?chat_id=<chat_id>
    """
    _validate_company_id(company_id)

    payload = {**data, "company": company_id}

    return await client.post(
        f"{COMPANY_JOBPOST_BASE_URL}/me/",
        params={"chat_id": chat_id},
        json=payload,
        headers=_build_bot_headers(),
    )


async def update_company_jobpost(
    chat_id: int,
    company_id: int,
    jobpost_id: int,
    data: Dict[str, Any],
) -> Any:
    """
    ویرایش آگهی شغلی.

    Backend:
        PATCH /api/crm/customer/company/jobpost/<jobpost_id>/?chat_id=<chat_id>&company=<company_id>
    """
    _validate_company_id(company_id)
    _validate_jobpost_id(jobpost_id)

    return await client.patch(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        params={"chat_id": chat_id, "company": company_id},
        json=data,
        headers=_build_bot_headers(),
    )


async def delete_company_jobpost(
    chat_id: int,
    company_id: int,
    jobpost_id: int,
) -> Any:
    """
    حذف آگهی شغلی.

    Backend:
        DELETE /api/crm/customer/company/jobpost/<jobpost_id>/?chat_id=<chat_id>&company=<company_id>
    """
    _validate_company_id(company_id)
    _validate_jobpost_id(jobpost_id)

    return await client.delete(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        params={"chat_id": chat_id, "company": company_id},
        headers=_build_bot_headers(),
    )


async def get_jobpost_choices() -> Any:
    """
    دریافت گزینه‌های فرم آگهی شغلی.

    Backend:
        GET /api/crm/customer/company/jobpost/choices/
    """
    return await client.get(
        f"{COMPANY_JOBPOST_BASE_URL}/choices/",
        headers=_build_bot_headers(),
    )
