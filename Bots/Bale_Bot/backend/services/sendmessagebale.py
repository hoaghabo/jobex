import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def get_bale_api_base_url() -> str:
    base_url = getattr(settings, "BALE_API_BASE_URL", "https://tapi.bale.ai")
    return base_url.rstrip("/")


def get_bale_bot_token() -> str:
    token = getattr(settings, "BALE_BOT_TOKEN", None)

    if not token:
        raise RuntimeError("BALE_BOT_TOKEN is not configured in Django settings")

    return token


def build_bale_api_url(method_name: str) -> str:
    base_url = get_bale_api_base_url()
    token = get_bale_bot_token()

    return f"{base_url}/bot{token}/{method_name}"


def post_bale_api(method_name: str, payload: dict) -> dict:
    url = build_bale_api_url(method_name)

    logger.info(
        "BALE API REQUEST method=%s chat_id=%s",
        method_name,
        payload.get("chat_id"),
    )

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception(
            "BALE API REQUEST FAILED method=%s chat_id=%s error=%s",
            method_name,
            payload.get("chat_id"),
            exc,
        )
        raise

    try:
        data = response.json()
    except ValueError:
        logger.exception(
            "BALE API INVALID JSON method=%s status=%s body=%s",
            method_name,
            response.status_code,
            response.text[:1000],
        )
        raise

    if isinstance(data, dict) and data.get("ok") is False:
        logger.error(
            "BALE API RETURNED OK_FALSE method=%s chat_id=%s response=%s",
            method_name,
            payload.get("chat_id"),
            data,
        )
        raise RuntimeError(f"Bale API returned ok=false for method={method_name}")

    logger.info(
        "BALE API SUCCESS method=%s chat_id=%s",
        method_name,
        payload.get("chat_id"),
    )

    return data


def send_bale_message(chat_id: str | int, text: str, reply_markup: dict | None = None) -> dict:
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    return post_bale_api("sendMessage", payload)
