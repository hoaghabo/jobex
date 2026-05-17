from app.infrastructure.backend.client import BackendClient, BackendAPIError
from app.config import settings

client = BackendClient()


COMPANY_JOBPOST_BASE_URL = "/api/crm/customer/company/jobpost"


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


async def get_choices_items(choice_group_name: str):
    """
    دریافت choiceهای مربوط به JobPosting

    Full URL:
    /api/crm/customer/company/jobpost/choices/
    """

    if not choice_group_name:
        return []

    try:
        response = await client.get(
            f"{COMPANY_JOBPOST_BASE_URL}/choices/",
            headers=_build_bot_headers(),
        )

        if not isinstance(response, dict):
            print("فرمت response نامعتبر است:", response)
            return []

        items = response.get(choice_group_name)

        if items is None:
            print(f"کلید '{choice_group_name}' در response وجود ندارد.")
            return []

        if not isinstance(items, list):
            print(f"مقدار کلید '{choice_group_name}' از نوع list نیست.")
            return []

        return items

    except BackendAPIError as e:
        print(f"خطا در دریافت choices برای '{choice_group_name}'")
        print("message:", e.message)
        print("status:", e.status_code)
        print("body:", e.body)
        return []

    except Exception as e:
        print(f"خطای غیرمنتظره در دریافت choices: {str(e)}")
        return []


async def create_company_jobpost(chat_id: int ,payload: dict):
    """
    ساخت آگهی شغلی جدید برای شرکت خود کاربر

    Backend URL:
    path("me/", MyCompanyJobPostingListCreateAPIView.as_view())

    Full URL:
    /api/crm/customer/company/jobpost/me/
    """

    return await client.post(
        f"{COMPANY_JOBPOST_BASE_URL}/me/",
        json=payload,
        params={"chat_id": chat_id},
        headers=_build_bot_headers(),
    )


async def get_company_jobpost_list(chat_id: int):
    """
    دریافت لیست آگهی‌های شرکت کاربر

    Full URL:
    /api/crm/customer/company/jobpost/me/
    """

    return await client.get(
        f"{COMPANY_JOBPOST_BASE_URL}/me/",
        params={"chat_id": chat_id},
        headers=_build_bot_headers(),
    )


async def get_company_jobpost_detail(chat_id: int, jobpost_id: int):
    """
    دریافت جزئیات یک آگهی

    Backend URL:
    path("<int:pk>/", MyCompanyJobPostingDetailAPIView.as_view())

    Full URL:
    /api/crm/customer/company/jobpost/<int:pk>/
    """

    return await client.get(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        params={"chat_id": chat_id},
        headers=_build_bot_headers(),
    )


async def patch_company_jobpost(jobpost_id: int, payload: dict):
    """
    ویرایش آگهی شغلی

    Full URL:
    /api/crm/customer/company/jobpost/<int:pk>/
    """

    return await client.patch(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        json=payload,
        headers=_build_bot_headers(),
    )


async def delete_company_jobpost(chat_id: int, jobpost_id: int):
    """
    حذف آگهی شغلی

    Full URL:
    /api/crm/customer/company/jobpost/<int:pk>/
    """

    return await client.delete(
        f"{COMPANY_JOBPOST_BASE_URL}/{jobpost_id}/",
        params={"chat_id": chat_id},
        headers=_build_bot_headers(),
    )
