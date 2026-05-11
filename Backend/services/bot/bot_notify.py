import requests
from django.conf import settings


def send_bale_text_message(chat_id, text, inline_keyboard=None):
    if not chat_id:
        return False

    url = f"https://tapi.bale.ai/bot{settings.BALE_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if inline_keyboard:
        payload["reply_markup"] = {
            "inline_keyboard": inline_keyboard
        }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except Exception:
        return False



def build_success_payment_text(payment):
    product_data = payment.product_data or {}

    product_name = (
        product_data.get("name")
        or product_data.get("title")
        or "محصول خریداری‌شده"
    )

    product_description = (
        product_data.get("description")
        or product_data.get("caption")
        or ""
    )

    amount_text = f"{payment.amount:,} تومان" if payment.amount else "-"

    text = (
        "✅ پرداخت شما با موفقیت انجام شد\n\n"
        f"📦 محصول: {product_name}\n"
    )

    if product_description:
        text += f"📝 توضیحات: {product_description}\n"

    text += (
        f"💰 مبلغ: {amount_text}\n"
        f"🧾 شناسه پرداخت: {payment.ref_id or '-'}"
    )

    return text



def notify_user_payment_success(payment):
    user = payment.user
    if not user:
        return

    chat_id = getattr(user, "chat_id", None) or getattr(user, "bale_chat_id", None)
    if not chat_id:
        return

    text = build_success_payment_text(payment)

    inline_keyboard = [
        [
            {"text": "📦 بسته‌های من", "callback_data": "my_packages"},
            {"text": "🏠 بازگشت به خانه", "callback_data": "home"},
        ]
    ]

    send_bale_text_message(
        chat_id=chat_id,
        text=text,
        inline_keyboard=inline_keyboard,
    )
