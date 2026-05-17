from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings

client = BackendClient()


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }



def format_campaign_requests(data: dict) -> str:
    results = data.get("results", [])

    if not results:
        return "📭 شما هنوز هیچ درخواستی برای کمپین ثبت نکرده‌اید."

    lines = []
    lines.append("📢 لیست درخواست‌های کمپین شما\n")

    status_map = {
        "user_request": "⏳ در انتظار بررسی",
        "approved": "✅ تایید شده",
        "rejected": "❌ رد شده",
    }

    for i, item in enumerate(results, start=1):

        channel = item.get("campaign_channel", {})
        title = channel.get("title", "نامشخص")
        key = channel.get("key", "-")
        status = status_map.get(item.get("status"), item.get("status"))

        lines.append(
            f"{i}. {title} ✉️\n"
            f"   نوع کمپین: {key}\n"
            f"   وضعیت: {status}\n"
        )

    lines.append("\n━━━━━━━━━━━━━━")
    lines.append(f"📊 مجموع درخواست‌ها: {data.get('count', len(results))}")

    return "\n".join(lines)


async def get_my_campaigns_list(chat_id: int):

    url = "/api/crm/customer/jobseeker/applications/campaign-channel/my-requests/"

    response = await client.get(
        url,
        headers=_build_bot_headers(),
        params={"chat_id": chat_id},
    )

    return response
