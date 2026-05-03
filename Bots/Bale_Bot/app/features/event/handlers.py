from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.features.event.api import (
    register_user_in_event,
    get_event_detail,
    create_event_payment,
    get_event_registration_status,
)

from app.features.event.message_utils import safe_edit_event_message

from app.features.event.views import (
    build_event_detail_view,
    build_events_list_view,
)

from app.features.event.keyboards import (
    event_payment_confirm_keyboard,
    event_after_payment_keyboard,
    back_to_event_detail_keyboard,
    event_registered_keyboard,
    event_payment_failed_keyboard,
)

router = Router()


@router.message(F.text == "📅 ایونت‌های جاری")
async def current_events_message_handler(message: Message) -> None:
    text, keyboard = await build_events_list_view()

    await message.answer(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "events:list")
async def events_list_callback_handler(callback: CallbackQuery) -> None:
    text, keyboard = await build_events_list_view()

    await safe_edit_event_message(
        callback=callback,
        text=text,
        reply_markup=keyboard,
        photo_url=None,
    )

    await callback.answer()


@router.callback_query(F.data == "event:list")
async def event_list_alias_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    text, keyboard = await build_events_list_view()

    await safe_edit_event_message(
        callback=callback,
        text=text,
        reply_markup=keyboard,
        photo_url=None,
    )


@router.callback_query(F.data.startswith("event:detail:"))
async def event_detail_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    event_id = callback.data.split(":")[-1]
    bale_user_id = callback.from_user.id

    try:
        text, keyboard, photo_url, photo_file_id = await build_event_detail_view(
            event_id=event_id,
            bale_user_id=bale_user_id,
        )
    except Exception as e:
        print("ERROR event_detail_callback_handler:", e)

        if callback.message:
            await callback.message.edit_text(
                text="خطا در دریافت جزئیات ایونت.",
                reply_markup=None,
            )
        return

    await safe_edit_event_message(
        callback=callback,
        text=text,
        reply_markup=keyboard,
        photo_url=photo_url,
        photo_file_id=photo_file_id,
    )


@router.callback_query(F.data.startswith("event:register:"))
async def event_register_callback_handler(callback: CallbackQuery) -> None:
    """
    کلیک روی دکمه ثبت‌نام ایونت.

    اگر ایونت رایگان باشد:
        ثبت‌نام مستقیم انجام می‌شود.

    اگر ایونت پولی باشد:
        ابتدا تایید ادامه پرداخت گرفته می‌شود.
        سپس در handler بعدی لینک زرین‌پال ساخته می‌شود.
    """

    event_id = callback.data.split(":")[-1]
    bale_user_id = callback.from_user.id

    try:
        event = await get_event_detail(
            event_id=event_id,
            bale_user_id=bale_user_id,
        )
    except Exception as e:
        print("ERROR event_register_callback_handler get_event_detail:", e)
        await callback.answer(
            "خطا در دریافت اطلاعات ایونت. لطفاً دوباره تلاش کنید.",
            show_alert=True,
        )
        return

    price = event.get("price") or 0

    try:
        price = int(price)
    except (TypeError, ValueError):
        price = 0

    title = event.get("title") or "ایونت"

    # ایونت رایگان
    if price <= 0:
        try:
            response = await register_user_in_event(
                event_id=event_id,
                bale_user_id=bale_user_id,
            )
        except Exception as e:
            print("ERROR event_register_callback_handler register free:", e)
            await callback.answer(
                "خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.",
                show_alert=True,
            )
            return

        registered = bool(response.get("registered", False))
        detail = response.get("detail") or "نتیجه ثبت‌نام مشخص نیست."

        if not registered:
            await callback.answer(detail, show_alert=True)
            return

        await callback.answer(detail, show_alert=True)

        try:
            text, keyboard, photo_url = await build_event_detail_view(
                event_id=event_id,
                bale_user_id=bale_user_id,
            )
        except Exception as e:
            print("ERROR event_register_callback_handler detail refresh:", e)
            return

        await safe_edit_event_message(
            callback=callback,
            text=text,
            reply_markup=keyboard,
            photo_url=photo_url,
        )

        return

    # ایونت پولی
    price_text = f"{price:,}"

    text = (
        "💳 ثبت‌نام در این ایونت نیاز به پرداخت دارد.\n\n"
        f"📌 ایونت: {title}\n"
        f"💰 مبلغ: {price_text} تومان\n\n"
        "آیا مایل به ادامه پرداخت هستید؟"
    )

    await safe_edit_event_message(
        callback=callback,
        text=text,
        reply_markup=event_payment_confirm_keyboard(event_id),
        photo_url=None,
    )

    await callback.answer()


@router.callback_query(F.data.startswith("event:payment_confirm:"))
async def event_payment_confirm_callback_handler(
    callback: CallbackQuery,
) -> None:
    """
    کاربر ادامه پرداخت را تایید کرده است.

    در flow زرین‌پال:
    1. بات از بک‌اند درخواست ساخت پرداخت می‌زند.
    2. بک‌اند Payment می‌سازد.
    3. بک‌اند از زرین‌پال authority/payment_url می‌گیرد.
    4. بات فقط payment_url را به کاربر نمایش می‌دهد.
    5. callback زرین‌پال مستقیم به بک‌اند می‌رود.
    6. بک‌اند verify می‌کند و ثبت‌نام را نهایی می‌کند.
    """

    event_id = callback.data.split(":")[-1]
    bale_user_id = callback.from_user.id

    try:
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id
        
        payment = await create_event_payment(
            event_id=event_id,
            bale_user_id=bale_user_id,
            bale_chat_id=chat_id,
            bale_payment_message_id=message_id,
        )

    except Exception as e:
        print("ERROR event_payment_confirm_callback_handler create payment:", e)
        await callback.answer(
            "خطا در ایجاد پرداخت. لطفاً دوباره تلاش کنید.",
            show_alert=True,
        )
        return

    if payment.get("already_registered"):
        await safe_edit_event_message(
            callback=callback,
            text="✅ شما قبلاً در این ایونت ثبت‌نام کرده‌اید.",
            reply_markup=event_registered_keyboard(event_id),
            photo_url=None,
        )
        await callback.answer()
        return

    if payment.get("is_free"):
        try:
            response = await register_user_in_event(
                event_id=event_id,
                bale_user_id=bale_user_id,
            )
        except Exception as e:
            print("ERROR event_payment_confirm_callback_handler register free:", e)
            await callback.answer(
                "خطا در ثبت‌نام رایگان.",
                show_alert=True,
            )
            return

        detail = response.get("detail") or "✅ ثبت‌نام شما با موفقیت انجام شد."

        await safe_edit_event_message(
            callback=callback,
            text=detail,
            reply_markup=event_registered_keyboard(event_id),
            photo_url=None,
        )
        await callback.answer()
        return

    payment_url = (
        payment.get("payment_url")
        or payment.get("url")
        or payment.get("startpay_url")
    )

    title = payment.get("title") or "ثبت‌نام ایونت"

    try:
        amount = int(payment.get("amount") or 0)
    except (TypeError, ValueError):
        amount = 0

    if not payment_url:
        await safe_edit_event_message(
            callback=callback,
            text=(
                "❌ لینک پرداخت از سمت درگاه دریافت نشد.\n\n"
                "لطفاً چند دقیقه بعد دوباره تلاش کنید."
            ),
            reply_markup=event_payment_failed_keyboard(event_id),
            photo_url=None,
        )
        await callback.answer(
            "لینک پرداخت معتبر نیست.",
            show_alert=True,
        )
        return

    amount_text = f"{amount:,}" if amount > 0 else "نامشخص"

    text = (
        "🧾 لینک پرداخت شما آماده است.\n\n"
        f"📌 ایونت: {title}\n"
        f"💰 مبلغ: {amount_text} تومان\n\n"
        "برای پرداخت، روی دکمه زیر بزنید و وارد درگاه زرین‌پال شوید.\n\n"
        "بعد از پرداخت موفق، ثبت‌نام شما توسط سیستم نهایی می‌شود.\n"
        "سپس می‌توانید با دکمه «بررسی وضعیت ثبت‌نام» وضعیت خود را چک کنید."
    )

    await safe_edit_event_message(
        callback=callback,
        text=text,
        reply_markup=event_after_payment_keyboard(
            event_id=event_id,
            payment_url=payment_url,
        ),
        photo_url=None,
    )

    await callback.answer()


@router.callback_query(F.data.startswith("event:payment_cancel:"))
async def event_payment_cancel_callback_handler(callback: CallbackQuery) -> None:
    """
    انصراف از پرداخت.
    """

    event_id = callback.data.split(":")[-1]

    await safe_edit_event_message(
        callback=callback,
        text=(
            "❌ پرداخت لغو شد.\n\n"
            "می‌توانید دوباره به جزئیات ایونت برگردید."
        ),
        reply_markup=back_to_event_detail_keyboard(event_id),
        photo_url=None,
    )

    await callback.answer()


@router.callback_query(F.data.startswith("event:payment_check:"))
async def event_payment_check_callback_handler(callback: CallbackQuery) -> None:
    """
    بررسی وضعیت ثبت‌نام بعد از پرداخت زرین‌پال.

    چون در زرین‌پال successful_payment داخل بات نداریم،
    این دکمه از بک‌اند می‌پرسد آیا callback/verify انجام شده
    و کاربر ثبت‌نام شده یا نه.
    """

    event_id = callback.data.split(":")[-1]
    bale_user_id = callback.from_user.id

    try:
        status = await get_event_registration_status(
            event_id=event_id,
            bale_user_id=bale_user_id,
        )
    except Exception as e:
        print("ERROR event_payment_check_callback_handler:", e)
        await callback.answer(
            "خطا در بررسی وضعیت. لطفاً دوباره تلاش کنید.",
            show_alert=True,
        )
        return

    is_registered = bool(
        status.get("registered")
        or status.get("is_registered")
    )

    if is_registered:
        await safe_edit_event_message(
            callback=callback,
            text=(
                "✅ ثبت‌نام شما با موفقیت نهایی شده است.\n\n"
                "🎉 شما در این ایونت ثبت‌نام شده‌اید."
            ),
            reply_markup=event_registered_keyboard(event_id),
            photo_url=None,
        )
        await callback.answer("ثبت‌نام شما تایید شد.", show_alert=True)
        return

    detail = (
        status.get("detail")
        or status.get("message")
        or "هنوز ثبت‌نامی برای شما ثبت نشده است. اگر همین الان پرداخت کرده‌اید، چند لحظه بعد دوباره بررسی کنید."
    )

    await callback.answer(detail, show_alert=True)


@router.callback_query(F.data == "event:noop")
async def event_noop_handler(callback: CallbackQuery) -> None:
    await callback.answer("این دکمه فقط برای نمایش وضعیت است.")
