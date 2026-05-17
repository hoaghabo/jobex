from app.infrastructure.backend.client import BackendAPIError
from app.infrastructure.backend.client import BackendClient
from app.config import settings

client = BackendClient()


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


