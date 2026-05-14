import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from app.config import settings
from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError

logger = logging.getLogger(__name__)

client = BackendClient()

PAYMENT_CREATE_ENDPOINT = "/api/billing/payments/create/"
CARD_RECEIPT_SUBMIT_ENDPOINT = "/api/billing/payments/card-to-card/submit-receipt/"
CARD_PAYMENT_APPROVE_ENDPOINT = "/api/billing/payments/card-to-card/approve/"
CARD_PAYMENT_REJECT_ENDPOINT = "/api/billing/payments/card-to-card/reject/"
BALE_WALLET_CONFIRM_ENDPOINT = "/api/billing/payments/bale-wallet/confirm/"


def _build_bot_headers() -> Dict[str, str]:
    """هدر احراز هویت ربات"""
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def _build_query_params(params: Dict[str, Any]) -> str:
    clean_params = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }

    if not clean_params:
        return ""

    return "?" + urlencode(clean_params)


def _payment_status_endpoint(payment_id: int) -> str:
    return f"/api/billing/payments/{payment_id}/status/"


async def create_payment(
    chat_id: str,
    product_id: int,
    payment_method: str,
) -> Dict[str, Any]:
    """
    ایجاد پرداخت جدید

    Args:
        chat_id: شناسه چت کاربر در بله
        product_id: شناسه محصول
        payment_method: روش پرداخت (zarinpal, card_to_card, bale_wallet)

    Returns:
        دیکشنری حاوی اطلاعات پرداخت

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    data = {
        "chat_id": chat_id,
        "product_id": product_id,
        "gateway": payment_method,
    }

    logger.info(
        f"ایجاد پرداخت برای محصول {product_id} با روش {payment_method} (chat_id={chat_id})"
    )

    try:
        result = await client.post(
            PAYMENT_CREATE_ENDPOINT,
            headers=_build_bot_headers(),
            json=data,
        )
        logger.info(f"پرداخت با موفقیت ایجاد شد: payment_id={result.get('id')}")
        logger.info(f"payment_create_response={result}")
        return result

    except BackendAPIError as e:
        logger.error(
            f"خطا در ایجاد پرداخت - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در ایجاد پرداخت: {str(e)}")
        raise


async def get_payment_status(
    chat_id: str,
    payment_id: int,
) -> Dict[str, Any]:
    """
    دریافت وضعیت پرداخت

    Returns:
        دیکشنری حاوی وضعیت پرداخت

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    params = {"chat_id": chat_id}
    url = _payment_status_endpoint(payment_id) + _build_query_params(params)

    logger.info(f"بررسی وضعیت پرداخت {payment_id} (chat_id={chat_id})")

    try:
        return await client.get(
            url,
            headers=_build_bot_headers(),
        )

    except BackendAPIError as e:
        logger.error(
            f"خطا در دریافت وضعیت پرداخت {payment_id} - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در دریافت وضعیت پرداخت {payment_id}: {str(e)}")
        raise


async def submit_card_receipt(
    chat_id: str,
    payment_id: int,
    receipt_file_id: str,
    tracking_code: Optional[str] = None,
    message_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    ارسال رسید کارت به کارت

    Args:
        chat_id: شناسه چت کاربر
        payment_id: شناسه پرداخت
        receipt_file_id: شناسه فایل بله
        tracking_code: کد پیگیری (اختیاری)
        message_id: شناسه پیام (اختیاری)

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    data = {
        "payment_id": payment_id,
        "receipt_file_id": receipt_file_id,
        "source": "bale",
        "chat_id": chat_id,
    }

    if tracking_code:
        data["receipt_tracking_code"] = tracking_code

    if message_id is not None:
        data["message_id"] = message_id

    logger.info(f"ارسال رسید برای پرداخت {payment_id} (chat_id={chat_id})")

    try:
        return await client.post(
            CARD_RECEIPT_SUBMIT_ENDPOINT,
            headers=_build_bot_headers(),
            json=data,
        )

    except BackendAPIError as e:
        logger.error(
            f"خطا در ارسال رسید پرداخت {payment_id} - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در ارسال رسید پرداخت {payment_id}: {str(e)}")
        raise


async def verify_payment(
    chat_id: str,
    payment_id: int,
    admin_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    تایید پرداخت کارت به کارت توسط ادمین

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    data = {
        "payment_id": payment_id,
    }

    if admin_notes:
        data["review_note"] = admin_notes

    logger.info(f"تایید پرداخت {payment_id} (chat_id={chat_id})")

    try:
        return await client.post(
            CARD_PAYMENT_APPROVE_ENDPOINT,
            headers=_build_bot_headers(),
            json=data,
        )

    except BackendAPIError as e:
        logger.error(
            f"خطا در تایید پرداخت {payment_id} - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در تایید پرداخت {payment_id}: {str(e)}")
        raise


async def reject_payment(
    chat_id: str,
    payment_id: int,
    admin_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    رد پرداخت کارت به کارت توسط ادمین

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    data = {
        "payment_id": payment_id,
    }

    if admin_notes:
        data["review_note"] = admin_notes

    logger.info(f"رد پرداخت {payment_id} (chat_id={chat_id})")

    try:
        return await client.post(
            CARD_PAYMENT_REJECT_ENDPOINT,
            headers=_build_bot_headers(),
            json=data,
        )

    except BackendAPIError as e:
        logger.error(
            f"خطا در رد پرداخت {payment_id} - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در رد پرداخت {payment_id}: {str(e)}")
        raise


async def confirm_bale_wallet_payment(
    chat_id: str,
    telegram_payment_charge_id: str,
    provider_payment_charge_id: str,
    invoice_payload: str,
    payment_id: Optional[str] = None,
    message_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    تایید پرداخت کیف پول بله

    Args:
        chat_id: شناسه چت کاربر
        payment_id: شناسه پرداخت
        telegram_payment_charge_id: شناسه تراکنش بله
        provider_payment_charge_id: شناسه تراکنش درگاه
        invoice_payload: payload فاکتور
        message_id: شناسه پیام (اختیاری)

    Returns:
        دیکشنری حاوی وضعیت پرداخت

    Raises:
        BackendAPIError: در صورت بروز خطا
    """
    data = {
        "telegram_payment_charge_id": telegram_payment_charge_id,
        "provider_payment_charge_id": provider_payment_charge_id,
        "invoice_payload": invoice_payload,
        "chat_id": chat_id,
    }

    if payment_id is not None:
        data["payment_id"] = payment_id

    if message_id is not None:
        data["message_id"] = message_id

    logger.info(f"🔑 Bot Token: {settings.BACKEND_BOT_API_TOKEN[:10]}...")
    logger.info(f"تایید پرداخت کیف پول بله {payment_id} (chat_id={chat_id})")

    try:
        return await client.post(
            BALE_WALLET_CONFIRM_ENDPOINT,
            headers=_build_bot_headers(),
            json=data,
        )

    except BackendAPIError as e:
        logger.error(
            f"خطا در تایید پرداخت کیف پول بله {payment_id} - message={e.message}, status={e.status_code}, body={e.body}"
        )
        raise

    except Exception as e:
        logger.exception(
            f"خطای غیرمنتظره در تایید پرداخت کیف پول بله {payment_id}: {str(e)}"
        )
        raise
