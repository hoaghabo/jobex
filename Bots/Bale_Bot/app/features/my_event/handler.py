from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.features.my_event.views import build_my_events_view

router = Router()


@router.message(F.text == "🎫 ایونت‌های ثبت‌نام‌شده من")
async def my_events_message_handler(message: Message) -> None:
    bale_user_id = message.from_user.id

    try:
        text, keyboard = await build_my_events_view(
            bale_user_id=bale_user_id,
        )
    except Exception as e:
        print("ERROR my_events_message_handler:", e)
        await message.answer("خطا در دریافت ایونت‌های ثبت‌نام‌شده.")
        return

    await message.answer(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "events:my")
async def my_events_callback_handler(callback: CallbackQuery) -> None:
    bale_user_id = callback.from_user.id

    try:
        text, keyboard = await build_my_events_view(
            bale_user_id=bale_user_id,
        )
    except Exception as e:
        print("ERROR my_events_callback_handler:", e)

        if callback.message:
            await callback.message.edit_text(
                text="خطا در دریافت ایونت‌های ثبت‌نام‌شده.",
                reply_markup=None,
            )

        await callback.answer()
        return

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    await callback.answer()
