import traceback
from io import BytesIO

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.features.adminpanel.registeredlist.api import (
    get_admin_events,
    get_event_registrations_excel,
    get_bale_id_from_message,
    get_bale_id_from_callback,
)
from app.features.auth.permissions import is_admin_user, is_registered_user
from app.infrastructure.backend.bot_user_api import get_user_status


router = Router()


async def check_admin_access_from_message(message: Message):
    try:
        status = await get_user_status(message)
        print("ADMIN STATUS RESULT =>", status)

    except Exception as e:
        print("Get user status error:", e)
        traceback.print_exc()
        return (
            False,
            None,
            "فعلاً امکان بررسی دسترسی شما وجود ندارد. لطفاً کمی بعد دوباره تلاش کنید.",
        )

    if not status:
        return (
            False,
            None,
            "شما دسترسی ادمین برای مشاهده لیست ثبت‌نامی‌ها ندارید یا ثبت‌نام شما کامل نشده است.",
        )

    if not is_registered_user(status) or not is_admin_user(status):
        return (
            False,
            status,
            "شما دسترسی ادمین برای مشاهده لیست ثبت‌نامی‌ها ندارید یا ثبت‌نام شما کامل نشده است.",
        )

    return True, status, None


@router.message(F.text == "👥 لیست ثبت‌نامی‌ها")
async def registered_list_entry(message: Message):
    allowed, status, error_message = await check_admin_access_from_message(message)

    if not allowed:
        await message.answer(error_message or "شما دسترسی لازم را ندارید.")
        return

    try:
        bale_id = get_bale_id_from_message(message)
        events = await get_admin_events(bale_id=bale_id)

    except Exception as e:
        print("Get admin events error:", e)
        traceback.print_exc()
        await message.answer("خطا در دریافت لیست ایونت‌ها از سرور.")
        return

    items = events.get("results", events) if isinstance(events, dict) else events

    if not items:
        await message.answer("هیچ ایونتی برای نمایش وجود ندارد.")
        return

    kb = InlineKeyboardBuilder()

    for event in items:
        event_id = event.get("id")
        title = (
            event.get("title")
            or event.get("name")
            or event.get("event_name")
            or f"ایونت {event_id}"
        )

        if not event_id:
            continue

        kb.button(
            text=title,
            callback_data=f"admin_registeredlist:{event_id}",
        )

    kb.adjust(1)

    await message.answer(
        "لطفاً ایونت موردنظر را انتخاب کنید:",
        reply_markup=kb.as_markup(),
    )


@router.callback_query(F.data.startswith("admin_registeredlist:"))
async def export_registered_list(callback: CallbackQuery):
    try:
        await callback.answer("در حال آماده‌سازی فایل...")

        # مهم:
        # اینجا نباید از callback.message.from_user استفاده شود.
        # کاربر واقعی callback.from_user است.
        bale_id = get_bale_id_from_callback(callback)

        event_id = int(callback.data.split(":")[1])

    except Exception as e:
        print("Callback parse error:", e)
        traceback.print_exc()
        await callback.message.answer("درخواست نامعتبر است.")
        return

    try:
        excel_response = await get_event_registrations_excel(
            event_id=event_id,
            bale_id=bale_id,
        )

    except Exception as e:
        print("Export registrations error:", e)
        traceback.print_exc()
        await callback.message.answer("خطا در دریافت فایل ثبت‌نامی‌ها از سرور.")
        return

    try:
        if not excel_response:
            await callback.message.answer("فایلی از سرور دریافت نشد.")
            return

        file_bytes = excel_response

        file = BufferedInputFile(
            file=file_bytes,
            filename=f"event_{event_id}_registrations.xlsx",
        )

        await callback.message.answer_document(
            document=file,
            caption="فایل لیست ثبت‌نامی‌های ایونت آماده شد.",
        )

    except Exception as e:
        print("Send excel file error:", e)
        traceback.print_exc()
        await callback.message.answer("خطا در ارسال فایل اکسل.")
