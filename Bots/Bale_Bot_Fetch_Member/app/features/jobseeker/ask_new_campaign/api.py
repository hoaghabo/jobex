from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings
import asyncio

client = BackendClient()
def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }
    

async def get_campaign_channels():
    try:
        response = await client.get(
            "/api/crm/customer/jobseeker/applications/campaign/",
            headers=_build_bot_headers()
        )

        if not isinstance(response, dict):
            print("فرمت response نامعتبر است:", response)
            return []

        results = response.get("results")

        if results is None:
            print("کلید results در response وجود ندارد.")
            return []

        if not isinstance(results, list):
            print("مقدار results از نوع list نیست.")
            return []

        return results

    except BackendAPIError as e:
        print("خطا در دریافت campaign channels")
        print("message:", e.message)
        print("status:", e.status_code)
        print("body:", e.body)
        return []

    except Exception as e:
        print(f"خطای غیرمنتظره: {str(e)}")
        return []


async def create_campaign_channel_ask(payload: dict):
    try:
        response = await client.post(
            "/api/crm/customer/jobseeker/applications/campaign-channel/ask/",
            json=payload,
            headers=_build_bot_headers()
        )

        return {
            "success": True,
            "data": response
        }

    except BackendAPIError as e:

        # خطای درخواست تکراری
        if e.status_code == 400 and "قبلاً" in str(e.body):
            return {
                "success": False,
                "type": "duplicate",
                "message": "شما قبلاً برای این کمپین درخواست ثبت کرده‌اید."
            }

        return {
            "success": False,
            "type": "backend_error",
            "message": "خطا در ثبت درخواست"
        }

    except Exception as e:
        return {
            "success": False,
            "type": "unknown",
            "message": "خطای غیرمنتظره"
        }
