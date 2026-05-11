# features/payment/api.py
import logging
from typing import Optional, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PaymentAPIError(Exception):
    """خطای سفارشی برای API پرداخت"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


def _bot_headers() -> Dict[str, str]:
    """هدر احراز هویت ربات"""
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


async def _safe_request(
    method: str,
    url: str,
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    درخواست HTTP با مدیریت خطای کامل
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=json_data)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            elif method.upper() == "PATCH":
                response = await client.patch(url, headers=headers, json=json_data)
            else:
                raise ValueError(f"متد HTTP پشتیبانی نمی‌شود: {method}")
            
            # بررسی وضعیت پاسخ
            if response.status_code >= 400:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get('detail', error_json)
                except:
                    pass
                
                logger.error(
                    f"خطای API: {method} {url} - Status {response.status_code} - {error_detail}"
                )
                raise PaymentAPIError(
                    message=f"خطای سرور: {error_detail}",
                    status_code=response.status_code,
                    response_data=error_detail
                )
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Timeout در درخواست به {url}")
        raise PaymentAPIError("زمان درخواست به پایان رسید. لطفاً دوباره تلاش کنید.")
    except httpx.NetworkError as e:
        logger.error(f"خطای شبکه در {url}: {str(e)}")
        raise PaymentAPIError("خطای اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید.")
    except PaymentAPIError:
        raise
    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در {url}: {str(e)}")
        raise PaymentAPIError(f"خطای غیرمنتظره: {str(e)}")


async def create_payment(
    base_url: str,
    chat_id: str,
    product_id: int,
    payment_method: str
) -> Dict[str, Any]:
    """
    ایجاد پرداخت جدید
    
    Args:
        base_url: آدرس پایه API
        chat_id: شناسه چت کاربر در بله
        product_id: شناسه محصول
        payment_method: روش پرداخت (zarinpal, card_to_card, bale_wallet)
    
    Returns:
        دیکشنری حاوی اطلاعات پرداخت
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/create/"
    data = {
        "chat_id": chat_id,
        "product_id": product_id,
        "gateway": payment_method
    }
    
    logger.info(f"ایجاد پرداخت برای محصول {product_id} با روش {payment_method} (chat_id={chat_id})")
    result = await _safe_request("POST", url, headers=_bot_headers(), json_data=data)
    logger.info(f"پرداخت با موفقیت ایجاد شد: payment_id={result.get('id')}")
    return result


async def get_payment_status(
    base_url: str,
    chat_id: str,
    payment_id: int
) -> Dict[str, Any]:
    """
    دریافت وضعیت پرداخت
    
    Returns:
        دیکشنری حاوی وضعیت پرداخت
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/{payment_id}/status/"
    params = {"chat_id": chat_id}
    
    logger.info(f"بررسی وضعیت پرداخت {payment_id} (chat_id={chat_id})")
    return await _safe_request("GET", url, headers=_bot_headers(), json_data=params)


async def submit_card_receipt(
    base_url: str,
    chat_id: str,
    payment_id: int,
    receipt_file_id: str,
    tracking_code: Optional[str] = None,
    message_id: Optional[int] = None
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
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/card-to-card/submit-receipt/"
    data = {
        "payment_id": payment_id,
        "receipt_file_id": receipt_file_id,
        "source": "bale",
        "chat_id": chat_id
    }
    
    if tracking_code:
        data["receipt_tracking_code"] = tracking_code
    
    if message_id:
        data["message_id"] = message_id
    
    logger.info(f"ارسال رسید برای پرداخت {payment_id} (chat_id={chat_id})")
    return await _safe_request("POST", url, headers=_bot_headers(), json_data=data)


async def verify_payment(
    base_url: str,
    chat_id: str,
    payment_id: int,
    admin_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    تایید پرداخت کارت به کارت توسط ادمین
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/card-to-card/approve/"
    data = {
        "payment_id": payment_id
    }
    if admin_notes:
        data["review_note"] = admin_notes
    
    logger.info(f"تایید پرداخت {payment_id} (chat_id={chat_id})")
    return await _safe_request("POST", url, headers=_bot_headers(), json_data=data)


async def reject_payment(
    base_url: str,
    chat_id: str,
    payment_id: int,
    admin_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    رد پرداخت کارت به کارت توسط ادمین
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/card-to-card/reject/"
    data = {
        "payment_id": payment_id
    }
    if admin_notes:
        data["review_note"] = admin_notes
    
    logger.info(f"رد پرداخت {payment_id} (chat_id={chat_id})")
    return await _safe_request("POST", url, headers=_bot_headers(), json_data=data)


async def confirm_bale_wallet_payment(
    base_url: str,
    chat_id: str,
    payment_id: Optional[str],
    telegram_payment_charge_id: str,
    provider_payment_charge_id: str,
    invoice_payload: str,
    message_id: Optional[int] = None,
) -> Dict[str, Any]:

    """
    تایید پرداخت کیف پول بله
    
    Args:
        base_url: آدرس پایه API
        chat_id: شناسه چت کاربر
        payment_id: شناسه پرداخت
        telegram_payment_charge_id: شناسه تراکنش بله
        provider_payment_charge_id: شناسه تراکنش درگاه
        invoice_payload: payload فاکتور
        message_id: شناسه پیام (اختیاری)
    
    Returns:
        دیکشنری حاوی وضعیت پرداخت
    
    Raises:
        PaymentAPIError: در صورت بروز خطا
    """
    url = f"{base_url}/api/billing/payments/bale-wallet/confirm/"
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
    return await _safe_request("POST", url, headers=_bot_headers(), json_data=data)
