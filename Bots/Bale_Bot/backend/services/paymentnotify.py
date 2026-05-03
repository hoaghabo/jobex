import logging
import requests

from django.conf import settings
from django.utils import timezone

from events.models import EventPayment

logger = logging.getLogger(__name__)


def model_has_field(instance, field_name):
    try:
        instance._meta.get_field(field_name)
        return True
    except Exception:
        return False


def get_bale_api_base_url():
    return settings.BALE_API_BASE_URL.rstrip("/")


def get_bale_api_url(method_name):
    return f"{get_bale_api_base_url()}/bot{settings.BALE_BOT_TOKEN}/{method_name}"


def post_bale_api(method_name, payload):
    url = get_bale_api_url(method_name)

    # برای اینکه توکن داخل لاگ نیفتد
    safe_url = f"{get_bale_api_base_url()}/bot***/{method_name}"

    logger.warning(
        "BALE API REQUEST method=%s url=%s payload=%s",
        method_name,
        safe_url,
        payload,
    )

    response = requests.post(url, json=payload, timeout=15)

    logger.warning(
        "BALE API RESPONSE method=%s status=%s body=%s",
        method_name,
        response.status_code,
        response.text,
    )

    response.raise_for_status()

    try:
        data = response.json()
    except Exception:
        logger.exception(
            "BALE API INVALID JSON method=%s response=%s",
            method_name,
            response.text,
        )
        raise

    # معمولاً Bot API خروجی ok دارد
    if isinstance(data, dict) and data.get("ok") is False:
        raise Exception(f"Bale API returned ok=false: {data}")

    return data


def send_bale_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return post_bale_api("sendMessage", payload)


def edit_bale_message_text(chat_id, message_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return post_bale_api("editMessageText", payload)


def delete_bale_message(chat_id, message_id):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }

    return post_bale_api("deleteMessage", payload)


def event_registered_reply_markup(event_id):
    """
    این callback_data ها را با هندلرهای بات خودت هماهنگ کن.
    اگر در باتت event:detail:{event_id} نداری، مقدارش را تغییر بده.
    """

    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ ثبت‌نام شده",
                    "callback_data": "event:noop",
                }
            ],
            [
                {
                    "text": "🔙 مشاهده رویداد",
                    "callback_data": f"event:detail:{event_id}",
                }
            ],
        ]
    }


def get_payment_chat_id(payment):
    user = payment.user

    chat_id = (
        getattr(payment, "bale_chat_id", None)
        or getattr(user, "bale_chat_id", None)
        or getattr(user, "chat_id", None)
        or getattr(user, "telegram_chat_id", None)
    )

    return chat_id


def get_payment_message_id(payment):
    return getattr(payment, "bale_payment_message_id", None)


def build_payment_success_text(payment):
    event_title = getattr(payment.event, "title", "رویداد")

    text = f"""
✅ پرداخت شما با موفقیت ثبت شد.

ثبت‌نام شما در رویداد زیر نهایی شد:

{event_title}

کد پیگیری:
{payment.ref_id or "-"}
""".strip()

    return text


def append_payment_error(payment, message):
    if not model_has_field(payment, "error_message"):
        logger.error(
            "PAYMENT ERROR FIELD NOT FOUND payment_id=%s message=%s",
            payment.id,
            message,
        )
        return

    payment.error_message = f"{payment.error_message or ''}\n{message}"
    payment.save(update_fields=["error_message"])


def mark_payment_as_bot_notified(payment):
    update_fields = []

    if model_has_field(payment, "bot_notified"):
        payment.bot_notified = True
        update_fields.append("bot_notified")

    if model_has_field(payment, "bot_notified_at"):
        payment.bot_notified_at = timezone.now()
        update_fields.append("bot_notified_at")

    if update_fields:
        payment.save(update_fields=update_fields)


def notify_payment_success_to_user(payment_id):
    logger.warning("NOTIFY START payment_id=%s", payment_id)

    payment = (
        EventPayment.objects
        .select_related("event", "user")
        .filter(id=payment_id)
        .first()
    )

    if not payment:
        logger.error("NOTIFY FAILED payment not found payment_id=%s", payment_id)
        return

    logger.warning(
        "NOTIFY PAYMENT FOUND payment_id=%s status=%s bot_notified=%s bale_chat_id=%s bale_message_id=%s",
        payment.id,
        payment.status,
        getattr(payment, "bot_notified", None),
        getattr(payment, "bale_chat_id", None),
        getattr(payment, "bale_payment_message_id", None),
    )

    if payment.status != EventPayment.STATUS_PAID:
        logger.warning(
            "NOTIFY SKIPPED payment is not paid payment_id=%s status=%s",
            payment.id,
            payment.status,
        )
        return

    if getattr(payment, "bot_notified", False):
        logger.warning(
            "NOTIFY SKIPPED already bot_notified payment_id=%s",
            payment.id,
        )
        return

    user = payment.user

    logger.warning(
        "NOTIFY USER user_id=%s user=%s",
        getattr(user, "id", None),
        user,
    )

    chat_id = get_payment_chat_id(payment)
    payment_message_id = get_payment_message_id(payment)

    logger.warning(
        "NOTIFY TARGET payment_id=%s chat_id=%s message_id=%s",
        payment.id,
        chat_id,
        payment_message_id,
    )

    if not chat_id:
        message = "Bot notify failed: payment/user has no bale_chat_id/chat_id"
        logger.error(
            "NOTIFY FAILED payment_id=%s reason=%s",
            payment.id,
            message,
        )
        append_payment_error(payment, message)
        return

    text = build_payment_success_text(payment)
    reply_markup = event_registered_reply_markup(payment.event_id)

    try:
        result = None

        if payment_message_id:
            try:
                logger.warning(
                    "NOTIFY TRY EDIT MESSAGE payment_id=%s chat_id=%s message_id=%s",
                    payment.id,
                    chat_id,
                    payment_message_id,
                )

                result = edit_bale_message_text(
                    chat_id=chat_id,
                    message_id=payment_message_id,
                    text=text,
                    reply_markup=reply_markup,
                )

                logger.warning(
                    "NOTIFY EDIT SUCCESS payment_id=%s result=%s",
                    payment.id,
                    result,
                )

            except Exception as edit_exc:
                logger.exception(
                    "NOTIFY EDIT FAILED payment_id=%s chat_id=%s message_id=%s error=%s",
                    payment.id,
                    chat_id,
                    payment_message_id,
                    edit_exc,
                )

                logger.warning(
                    "NOTIFY FALLBACK SEND MESSAGE payment_id=%s chat_id=%s",
                    payment.id,
                    chat_id,
                )

                result = send_bale_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                )

                logger.warning(
                    "NOTIFY FALLBACK SEND SUCCESS payment_id=%s result=%s",
                    payment.id,
                    result,
                )

        else:
            logger.warning(
                "NOTIFY SEND NEW MESSAGE because message_id is empty payment_id=%s chat_id=%s",
                payment.id,
                chat_id,
            )

            result = send_bale_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
            )

            logger.warning(
                "NOTIFY SEND SUCCESS payment_id=%s result=%s",
                payment.id,
                result,
            )

        mark_payment_as_bot_notified(payment)

        logger.warning(
            "NOTIFY SUCCESS payment_id=%s bale_result=%s",
            payment.id,
            result,
        )

    except Exception as exc:
        logger.exception(
            "NOTIFY EXCEPTION payment_id=%s error=%s",
            payment.id,
            exc,
        )

        append_payment_error(
            payment,
            f"Bot notify failed: {exc}",
        )
