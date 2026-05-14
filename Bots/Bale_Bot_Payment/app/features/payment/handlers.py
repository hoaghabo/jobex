# app/features/payment/handlers.py
import logging
import os
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .api import (
    create_payment,
    get_payment_status,
    submit_card_receipt,
    confirm_bale_wallet_payment,
)
from .keyboards import (
    get_payment_methods_keyboard,
    get_payment_actions_keyboard,
    get_back_to_payment_keyboard,
    get_payment_success_keyboard
)
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings
from app.infrastructure.backend.bot_user_api import get_user_status_by_chat_id

logger = logging.getLogger(__name__)
router = Router()


class PaymentStates(StatesGroup):
    """حالت‌های FSM برای پرداخت"""
    waiting_card_receipt = State()
    waiting_tracking_code = State()


def is_bale_member(backend_response: dict | None) -> bool:
    """
    بررسی عضویت کاربر در بله از طریق بک‌اند.
    اگر chat_id کاربر در مدل BotBaleMember موجود باشد، عضو محسوب می‌شود.
    """
    if not backend_response:
        return False

    if backend_response.get("is_bot_bale_member") is True:
        return True

    if backend_response.get("is_registered") is True:
        return True

    if backend_response.get("registered") is True:
        return True

    user_data = backend_response.get("user")
    if isinstance(user_data, dict):
        if user_data.get("is_bot_bale_member") is True:
            return True

        if user_data.get("is_registered") is True:
            return True

        if user_data.get("registered") is True:
            return True

    return False


async def check_user_bale_membership(callback: CallbackQuery) -> bool:
    """
    بررسی عضویت کاربر در بله از طریق بک‌اند.
    """
    try:
        user_chat_id = callback.from_user.id
        status_response = await get_user_status_by_chat_id(user_chat_id)
        logger.info(f"Status response for user {user_chat_id}: {status_response}")
        return is_bale_member(status_response)
    except Exception as e:
        logger.error(f"خطا در بررسی عضویت بله: {e}")
        return False


def build_success_payment_text(
    product_name: str | None = None,
    product_description: str | None = None,
    amount: int | str | None = None,
    payment_id: int | str | None = None,
    extra_text: str | None = None
) -> str:
    product_name = product_name or "محصول خریداری‌شده"
    product_description = product_description or ""

    try:
        amount_value = int(amount or 0)
        amount_text = f"{amount_value:,} تومان"
    except Exception:
        amount_text = f"{amount or 0} تومان"

    text = (
        f"✅ *پرداخت شما با موفقیت تایید شد!*\n\n"
        f"🎉 محصول شما فعال شد.\n\n"
        f"📦 محصول: *{product_name}*\n"
    )

    if product_description:
        desc = (
            product_description[:150] + "..."
            if len(product_description) > 150
            else product_description
        )
        text += f"📝 توضیحات: {desc}\n"

    text += f"💰 مبلغ پرداختی: *{amount_text}*\n"

    if payment_id is not None:
        text += f"🔢 شناسه پرداخت: `{payment_id}`\n"

    if extra_text:
        text += f"\n{extra_text}"
    else:
        text += "\nاز دکمه‌های زیر می‌توانید بسته‌های خود را مشاهده کنید یا به خانه برگردید."

    return text


async def auto_check_payment_status(
    bot,
    chat_id: int | str,
    payment_id: int,
    message_id: int,
    max_attempts: int = 12,
    interval: int = 5
):
    """
    بررسی خودکار وضعیت پرداخت زرین‌پال و ویرایش همان پیام قبلی
    """
    for attempt in range(max_attempts):
        await asyncio.sleep(interval)

        try:
            status_data = await get_payment_status(
                chat_id=str(chat_id),
                payment_id=payment_id
            )

            status = status_data.get("status", "unknown")
            product_name = status_data.get("product_name") or status_data.get("title") or "محصول"
            product_description = status_data.get("product_description") or status_data.get("description") or ""
            amount = status_data.get("amount", 0)
            product_id = status_data.get("product_id")

            if status == "completed":
                success_text = build_success_payment_text(
                    product_name=product_name,
                    product_description=product_description,
                    amount=amount,
                    payment_id=payment_id
                )

                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=success_text,
                    parse_mode="Markdown",
                    reply_markup=get_payment_success_keyboard()
                )
                return

            elif status == "failed":
                fail_text = (
                    f"❌ *پرداخت ناموفق*\n\n"
                    f"متأسفانه پرداخت شما تکمیل نشد.\n\n"
                    f"📦 محصول: *{product_name}*\n"
                    f"💰 مبلغ: *{amount:,} تومان*\n"
                    f"🔢 شناسه پرداخت: `{payment_id}`\n\n"
                    f"💡 می‌توانید دوباره تلاش کنید."
                )

                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=fail_text,
                    parse_mode="Markdown",
                    reply_markup=get_back_to_payment_keyboard(product_id)
                )
                return

        except Exception as e:
            logger.error(f"خطا در بررسی خودکار وضعیت پرداخت {payment_id}: {e}")
            continue

    try:
        timeout_text = (
            f"⏰ *در حال بررسی پرداخت*\n\n"
            f"پرداخت شما هنوز در حال پردازش است.\n\n"
            f"🔢 شناسه پرداخت: `{payment_id}`\n\n"
            f"📌 می‌توانید با دکمه زیر وضعیت را دوباره بررسی کنید."
        )

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=timeout_text,
            parse_mode="Markdown",
            reply_markup=get_payment_actions_keyboard(payment_id, "ZIBAL")
        )
    except Exception as e:
        logger.error(f"خطا در ویرایش پیام timeout: {e}")


# ==================== انتخاب روش پرداخت ====================

@router.callback_query(F.data.startswith("pay_product:"))
async def choose_payment_method(callback: CallbackQuery, state: FSMContext):
    """نمایش روش‌های پرداخت"""
    await callback.answer()

    try:
        product_id = int(callback.data.split(":")[1])
        await state.update_data(product_id=product_id)

        text = (
            "💳 *انتخاب روش پرداخت*\n\n"
            "لطفاً یکی از روش‌های پرداخت زیر را انتخاب کنید:"
        )

        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_payment_methods_keyboard(product_id)
        )

    except Exception as e:
        logger.exception(f"خطا در انتخاب روش پرداخت: {e}")
        try:
            await callback.message.answer("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass


# ==================== زیبال ====================

@router.callback_query(F.data.startswith("payment_method:zibal:"))
async def handle_ZIBAL_payment(callback: CallbackQuery, state: FSMContext):
    """پرداخت با زرین‌پال"""
    await callback.answer()

    product_id = None

    try:
        is_member = await check_user_bale_membership(callback)
        if not is_member:
            await callback.message.edit_text(
                "❌ *دسترسی محدود*\n\n"
                "برای استفاده از این بخش، ابتدا باید عضو بله شوید.",
                parse_mode="Markdown"
            )
            return

        product_id = int(callback.data.split(":")[2])
        chat_id = str(callback.from_user.id)

        await callback.message.edit_text("⏳ در حال آماده‌سازی درگاه پرداخت...")

        payment_data = await create_payment(
            chat_id=chat_id,
            product_id=product_id,
            payment_method="zibal"
        )

        payment_id = payment_data.get("id")
        payment_url = payment_data.get("payment_url")
        product_name = payment_data.get("product_name", "محصول")
        product_description = payment_data.get("product_description", "")
        amount = payment_data.get("amount", 0)
        
        logger.info(f"==============> {payment_url}")

        if not payment_url:
            await callback.message.edit_text(
                "❌ خطا در ایجاد درگاه پرداخت\n\n"
                "لطفاً با پشتیبانی تماس بگیرید.",
                reply_markup=get_back_to_payment_keyboard(product_id)
            )
            return

        text = (
            f"💳 *پرداخت آنلاین - زیبال*\n\n"
            f"📦 محصول: *{product_name}*\n"
        )

        if product_description:
            desc = (
                product_description[:100] + "..."
                if len(product_description) > 100
                else product_description
            )
            text += f"📝 {desc}\n\n"
        else:
            text += "\n"

        text += (
            f"💰 مبلغ قابل پرداخت: *{amount:,} تومان*\n"
            f"🔢 شناسه پرداخت: `{payment_id}`\n\n"
            f"🔐 پرداخت از طریق درگاه امن زیبال\n"
            f"✅ پس از پرداخت، وضعیت به صورت خودکار بررسی می‌شود."
        )

        sent_message = await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_payment_actions_keyboard(payment_id, "zibal", payment_url),
            disable_web_page_preview=True
        )

        await state.update_data(
            payment_id=payment_id,
            product_id=product_id,
            payment_message_id=sent_message.message_id
        )

        asyncio.create_task(
            auto_check_payment_status(
                bot=callback.bot,
                chat_id=callback.message.chat.id,
                payment_id=payment_id,
                message_id=sent_message.message_id
            )
        )

    except BackendAPIError as e:
        logger.error(f"خطای API در زرین‌پال: {e.message}")
        try:
            await callback.message.edit_text(
                f"❌ خطا در ایجاد پرداخت\n\n"
                f"📌 {e.message}\n\n"
                f"لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                reply_markup=get_back_to_payment_keyboard(product_id) if product_id else None
            )
        except Exception as edit_error:
            logger.error(f"خطا در ویرایش پیام: {edit_error}")

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در زرین‌پال: {e}")
        try:
            await callback.message.answer("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment_status_handler(callback: CallbackQuery, state: FSMContext):
    """بررسی وضعیت پرداخت"""
    await callback.answer("⏳ در حال بررسی...")

    try:
        is_member = await check_user_bale_membership(callback)
        if not is_member:
            await callback.message.edit_text(
                "❌ *دسترسی محدود*\n\n"
                "برای استفاده از این بخش، ابتدا باید عضو بله شوید.",
                parse_mode="Markdown"
            )
            return

        payment_id = int(callback.data.split(":")[1])
        chat_id = str(callback.from_user.id)

        status_data = await get_payment_status(
            chat_id=chat_id,
            payment_id=payment_id
        )

        status = status_data.get("status", "unknown")
        status_display = status_data.get("status_display", status)
        product_name = status_data.get("product_name", "محصول")
        product_description = status_data.get("product_description", "")
        amount = status_data.get("amount", 0)
        product_id = status_data.get("product_id")

        if status == "completed":
            text = build_success_payment_text(
                product_name=product_name,
                product_description=product_description,
                amount=amount,
                payment_id=payment_id
            )
            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=get_payment_success_keyboard()
            )
            return

        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫",
            "awaiting_verification": "⏰"
        }.get(status, "❓")

        text = f"{status_emoji} *وضعیت پرداخت: {status_display}*\n\n"
        text += f"📦 محصول: *{product_name}*\n"

        if product_description:
            desc = (
                product_description[:120] + "..."
                if len(product_description) > 120
                else product_description
            )
            text += f"📝 {desc}\n"

        text += f"💰 مبلغ: *{amount:,} تومان*\n"
        text += f"🔢 شناسه: `{payment_id}`\n\n"

        if status == "failed":
            text += "❌ پرداخت ناموفق بود.\n💡 می‌توانید دوباره تلاش کنید."
            reply_markup = get_back_to_payment_keyboard(product_id)
        elif status == "awaiting_verification":
            text += "⏰ در انتظار تایید است.\n📌 پس از بررسی، نتیجه اطلاع داده می‌شود."
            reply_markup = None
        elif status == "pending":
            text += "⏳ در انتظار پرداخت.\n💡 لطفاً پرداخت را تکمیل کنید."
            reply_markup = get_payment_actions_keyboard(payment_id, "zibal")
        else:
            reply_markup = None

        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except BackendAPIError as e:
        logger.error(f"خطای API در بررسی وضعیت: {e.message}")
        try:
            await callback.message.answer(f"❌ {e.message}")
        except Exception:
            pass
    except Exception as e:
        logger.exception(f"خطا در بررسی وضعیت: {e}")
        try:
            await callback.message.answer("❌ خطایی رخ داد.")
        except Exception:
            pass


# ==================== کارت به کارت ====================

@router.callback_query(F.data.startswith("payment_method:card_to_card:"))
async def handle_card_to_card_payment(callback: CallbackQuery, state: FSMContext):
    """پرداخت کارت به کارت"""
    await callback.answer()

    product_id = None

    try:
        is_member = await check_user_bale_membership(callback)
        if not is_member:
            await callback.message.edit_text(
                "❌ *دسترسی محدود*\n\n"
                "برای استفاده از این بخش، ابتدا باید عضو بله شوید.",
                parse_mode="Markdown"
            )
            return

        product_id = int(callback.data.split(":")[2])
        chat_id = str(callback.from_user.id)

        await callback.message.edit_text("⏳ در حال آماده‌سازی...")

        payment_data = await create_payment(
            chat_id=chat_id,
            product_id=product_id,
            payment_method="card_to_card"
        )

        payment_id = payment_data.get("id")
        amount = payment_data.get("amount", 0)
        product_name = payment_data.get("product_name", "محصول")
        product_description = payment_data.get("product_description", "")

        card_info = payment_data.get("card_to_card", {})
        card_number = card_info.get("card_number") or os.getenv("CARD_NUMBER", "شماره کارت تنظیم نشده")
        card_holder = card_info.get("card_holder") or os.getenv("CARD_HOLDER", "نام صاحب کارت تنظیم نشده")

        await state.update_data(payment_id=payment_id, product_id=product_id)
        await state.set_state(PaymentStates.waiting_card_receipt)

        text = (
            f"💳 *پرداخت کارت به کارت*\n\n"
            f"📦 محصول: *{product_name}*\n"
        )

        if product_description:
            desc = (
                product_description[:100] + "..."
                if len(product_description) > 100
                else product_description
            )
            text += f"📝 {desc}\n\n"
        else:
            text += "\n"

        text += (
            f"💰 مبلغ قابل پرداخت: *{amount:,} تومان*\n"
            f"🔢 شناسه پرداخت: `{payment_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📌 *اطلاعات کارت مقصد:*\n\n"
            f"💳 شماره کارت:\n`{card_number}`\n\n"
            f"👤 به نام: *{card_holder}*\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📸 *مراحل بعدی:*\n"
            f"1️⃣ مبلغ را به کارت بالا واریز کنید\n"
            f"2️⃣ تصویر رسید را در همین چت ارسال کنید\n"
            f"3️⃣ منتظر تایید ادمین باشید\n\n"
            f"⚠️ حتماً مبلغ دقیق را واریز کنید"
        )

        await callback.message.edit_text(text, parse_mode="Markdown")

    except BackendAPIError as e:
        logger.error(f"خطای API در کارت به کارت: {e.message}")
        try:
            await callback.message.edit_text(
                f"❌ خطا در ایجاد پرداخت\n\n{e.message}",
                reply_markup=get_back_to_payment_keyboard(product_id) if product_id else None
            )
        except Exception:
            pass
    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در کارت به کارت: {e}")
        try:
            await callback.message.answer("❌ خطایی رخ داد.")
        except Exception:
            pass


@router.message(PaymentStates.waiting_card_receipt, F.photo)
async def handle_receipt_photo(message: Message, state: FSMContext):
    """دریافت تصویر رسید"""
    try:
        user_data = await state.get_data()
        payment_id = user_data.get("payment_id")
        chat_id = str(message.from_user.id)

        if not payment_id:
            await message.answer("❌ خطا: اطلاعات پرداخت یافت نشد. لطفاً دوباره شروع کنید.")
            await state.clear()
            return

        photo = message.photo[-1]
        file_id = photo.file_id

        await message.answer("⏳ در حال ارسال رسید به سیستم...")

        await submit_card_receipt(
            chat_id=chat_id,
            payment_id=payment_id,
            receipt_file_id=file_id,
            message_id=message.message_id
        )

        success_text = (
            f"✅ *رسید شما ثبت شد!*\n\n"
            f"🔢 شناسه پرداخت: `{payment_id}`\n"
            f"⏰ وضعیت: *در انتظار تایید ادمین*\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📌 رسید شما در حال بررسی است\n"
            f"✅ پس از تایید، محصول فعال می‌شود\n"
            f"📬 نتیجه از طریق پیام اطلاع داده می‌شود\n\n"
            f"⏱ زمان بررسی: معمولاً کمتر از 2 ساعت"
        )

        await message.answer(success_text, parse_mode="Markdown")
        await state.clear()

    except BackendAPIError as e:
        logger.error(f"خطای API در ارسال رسید: {e.message}")
        await message.answer(
            f"❌ خطا در ثبت رسید\n\n{e.message}\n\n"
            f"💡 لطفاً دوباره تصویر را ارسال کنید"
        )
    except Exception as e:
        logger.exception(f"خطا در دریافت رسید: {e}")
        await message.answer("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")


@router.message(PaymentStates.waiting_card_receipt)
async def invalid_receipt_format(message: Message):
    """پیام نامعتبر به جای تصویر"""
    await message.answer(
        "❌ *فرمت نامعتبر*\n\n"
        "لطفاً فقط *تصویر رسید* را ارسال کنید\n\n"
        "📸 عکس باید واضح و خوانا باشد",
        parse_mode="Markdown"
    )


# ==================== کیف پول بله ====================

@router.callback_query(F.data.startswith("payment_method:bale_wallet:"))
async def handle_bale_wallet_payment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    product_id = None

    try:
        is_member = await check_user_bale_membership(callback)
        if not is_member:
            await callback.message.edit_text(
                "❌ *دسترسی محدود*\n\n"
                "برای استفاده از این بخش، ابتدا باید عضو بله شوید.",
                parse_mode="Markdown"
            )
            return

        product_id = int(callback.data.split(":")[2])
        chat_id = str(callback.from_user.id)

        payment_data = await create_payment(
            chat_id=chat_id,
            product_id=product_id,
            payment_method="bale_wallet"
        )

        payment_id = payment_data.get("id")
        bale_wallet_data = payment_data.get("bale_wallet", {})
        invoice_message_id = bale_wallet_data.get("message_id")
        invoice_sent = bale_wallet_data.get("invoice_sent", False)

        if not invoice_message_id or not invoice_sent:
            await callback.message.edit_text(
                "❌ خطا در ارسال فاکتور پرداخت\n\n"
                "لطفاً دوباره تلاش کنید.",
                reply_markup=get_back_to_payment_keyboard(product_id)
            )
            return

        await state.update_data(payment_id=payment_id, product_id=product_id)

        try:
            await callback.message.delete()
        except Exception as delete_error:
            logger.warning(f"عدم امکان حذف پیام انتخاب روش پرداخت: {delete_error}")

    except BackendAPIError as e:
        logger.error(f"خطای API در کیف پول بله: {e.message}")
        try:
            await callback.message.edit_text(
                f"❌ خطا در ایجاد پرداخت\n\n{e.message}",
                reply_markup=get_back_to_payment_keyboard(product_id) if product_id else None
            )
        except Exception:
            pass

    except Exception as e:
        logger.exception(f"خطای غیرمنتظره در کیف پول بله: {e}")
        try:
            await callback.message.edit_text(
                "❌ خطایی رخ داد.",
                reply_markup=get_back_to_payment_keyboard(product_id) if product_id else None
            )
        except Exception:
            pass


# ==================== Pre-Checkout Query Handler ====================

@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """
    پاسخ به PreCheckoutQuery بله
    """
    try:
        invoice_payload = pre_checkout_query.invoice_payload
        logger.info(f"PreCheckoutQuery received: {invoice_payload}")

        await pre_checkout_query.answer(ok=True)
        logger.info(f"PreCheckoutQuery answered successfully for payload: {invoice_payload}")

    except Exception as e:
        logger.error(f"خطا در پاسخ به PreCheckoutQuery: {e}")
        await pre_checkout_query.answer(
            ok=False,
            error_message="خطا در پردازش پرداخت. لطفاً دوباره تلاش کنید."
        )


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message):
    try:
        payment_info = message.successful_payment
        invoice_payload = payment_info.invoice_payload
        telegram_payment_charge_id = payment_info.telegram_payment_charge_id
        provider_payment_charge_id = payment_info.provider_payment_charge_id or ""

        logger.info(
            f"✅ Successful payment received: "
            f"payload={invoice_payload}, "
            f"telegram_charge_id={telegram_payment_charge_id}, "
            f"provider_charge_id={provider_payment_charge_id}"
        )

        payment_id = None
        try:
            parts = invoice_payload.split("_")
            if parts[0] == "payment":
                payment_id = int(parts[1])
        except (IndexError, ValueError):
            logger.warning(
                f"⚠️ payload جدید نیست، فقط با invoice_payload تایید می‌کنیم: {invoice_payload}"
            )

        response = await confirm_bale_wallet_payment(
            chat_id=str(message.chat.id),
            payment_id=str(payment_id) if payment_id is not None else None,
            telegram_payment_charge_id=telegram_payment_charge_id,
            provider_payment_charge_id=provider_payment_charge_id,
            invoice_payload=invoice_payload,
            message_id=message.message_id,
        )

        if response.get("status") == "paid":
            product_name = None
            product_description = None
            amount = None

            if payment_id is not None:
                try:
                    status_data = await get_payment_status(
                        chat_id=str(message.chat.id),
                        payment_id=payment_id
                    )
                    product_name = status_data.get("product_name")
                    product_description = status_data.get("product_description")
                    amount = status_data.get("amount")

                except Exception as status_error:
                    logger.warning(
                        f"⚠️ خطا در دریافت اطلاعات پرداخت بعد از تایید کیف پول بله: {status_error}"
                    )

            product_name = (
                product_name
                or response.get("product_name")
                or response.get("product_title")
                or response.get("title")
                or "محصول خریداری‌شده"
            )

            product_description = (
                product_description
                or response.get("product_description")
                or response.get("description")
                or ""
            )

            amount = (
                amount
                or response.get("amount")
                or response.get("paid_amount")
                or response.get("final_amount")
                or 0
            )

            success_text = build_success_payment_text(
                product_name=product_name,
                product_description=product_description,
                amount=amount,
                payment_id=payment_id
            )

            await message.answer(
                success_text,
                parse_mode="Markdown",
                reply_markup=get_payment_success_keyboard()
            )

        else:
            await message.answer(
                "⚠️ پرداخت دریافت شد اما در حال بررسی است.\n\n"
                "لطفاً چند لحظه صبر کنید."
            )

    except BackendAPIError as e:
        logger.error(f"❌ خطای API در تایید پرداخت: {e.message}")
        await message.answer(
            f"⚠️ خطا در تایید پرداخت:\n\n{e.message}\n\n"
            "لطفاً با پشتیبانی تماس بگیرید."
        )
    except Exception as e:
        logger.error(f"❌ خطا در پردازش پرداخت موفق: {e}")
        await message.answer(
            "⚠️ پرداخت شما دریافت شد اما خطایی رخ داد.\n\n"
            "لطفاً با پشتیبانی تماس بگیرید."
        )
