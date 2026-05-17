from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings

client = BackendClient()


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def format_companies_list(data: dict) -> str:

    results = data.get("results", [])

    if not results:
        return "📭 هنوز هیچ شرکتی ثبت نکرده‌اید."

    lines = []
    lines.append("🏢 *لیست شرکت‌های شما*\n")

    for i, item in enumerate(results, start=1):

        name = item.get("company_name", "نامشخص")
        role = item.get("role_name", "-")

        lines.append(
            f"🔹 {i}. {name}\n"
            f"   👤 نقش شما: {role}\n"
        )

    lines.append("━━━━━━━━━━━━━━")
    lines.append(f"📊 مجموع شرکت‌ها: {data.get('count', len(results))}")

    return "\n".join(lines)





def format_single_company_info(data: dict) -> str:

    name = data.get("company_name", "نامشخص")
    role = data.get("role_name", "-")
    size = data.get("organization_size_label", "-")
    city = data.get("city_name", "-")
    industry = data.get("industry", "-")
    address = data.get("full_address", "-")
    website = data.get("website", "-")
    phone = data.get("landline_phone", "-")

    lines = []

    lines.append("🏢 *اطلاعات شرکت*\n")

    lines.append(f"🏢 نام شرکت: {name}")
    lines.append(f"👤 نقش شما: {role}")
    lines.append(f"👥 اندازه سازمان: {size}")
    lines.append(f"🏭 صنعت: {industry}")
    lines.append(f"📍 شهر: {city}")
    lines.append(f"📌 آدرس: {address}")
    lines.append(f"☎️ تلفن: {phone}")
    lines.append(f"🌐 وبسایت: {website}")

    lines.append("━━━━━━━━━━━━━━")

    return "\n".join(lines)



async def get_my_company_list(chat_id: int):

    url = f"/api/crm/customer/company/profile/me/"

    response = await client.get(
        url,
        headers=_build_bot_headers(),
        params={"chat_id": chat_id},
    )

    return response



async def get_my_company_id(chat_id: int , company_id: int):

    url = f"/api/crm/customer/company/profile/me/{company_id}/"

    response = await client.get(
        url,
        headers=_build_bot_headers(),
        params={"chat_id": chat_id},
    )

    return response



async def edit_my_company_info(chat_id: int, company_id: int, payload: dict):

    url = f"/api/crm/customer/company/profile/me/{company_id}/"

    response = await client.patch(
        url,
        json=payload,
        headers=_build_bot_headers(),
        params={"chat_id": chat_id},
    )

    return response
