from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings
client = BackendClient()
def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }
    

async def get_choices_items(choice_group_name):
    if not choice_group_name:
        return []

    try:
        response = await client.get("/api/crm/customer/jobseeker/profile/choices/")

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
        print(f"خطای غیرمنتظره: {str(e)}")
        return []
