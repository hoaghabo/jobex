from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.infrastructure.backend.bot_user_api import get_user_status
from app.features.auth.permissions import (
    extract_menu_flags
)
from app.features.auth.states import RegisterStates
from .keyboards import get_campaign_request_inline_keyboard
from .state import ResumeJobSeekerAskCampaignsStates
from .api import get_campaign_channels , create_campaign_channel_ask
from app.features.jobseeker.jobseeker_main.keyboards import get_jobseeker_main_menu



router = Router()

@router.message(F.text == "درخواست کمپین جدید")
async def choose_jobseeker_handler(message: Message, state: FSMContext):
    # -------------------------------------------------
    # 1) گرفتن وضعیت کاربر
    # -------------------------------------------------
    try:
        status_response = await get_user_status(message)
    except Exception as e:
        print("Get user status error:", e)
        await message.answer(
            "خطا در دریافت اطلاعات کاربر. لطفاً دوباره تلاش کنید."
        )
        return

    menu_flags = extract_menu_flags(status_response)

    is_registered = menu_flags.get("is_bot_bale_member", False)
    is_jobseeker_member = menu_flags.get("is_jobseeker_member", False)

    # -------------------------------------------------
    # حالت اول: کاربر هنوز ثبت‌نام نکرده
    # -------------------------------------------------
    if not is_registered:
        await message.answer(
            "ابتدا باید ثبت‌نام کنید.\n"
            "لطفاً نام و نام خانوادگی خود را وارد کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegisterStates.waiting_for_full_name)
        return
    remove_msg = await message.answer(
        "---------------------------درخواست کمپین جدید------------------------",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "کارجوی گرامی لطفا کمپین مدنظر خود را انتخاب کنید:",
        reply_markup = await get_campaign_request_inline_keyboard()
    )
    
    await state.set_state(ResumeJobSeekerAskCampaignsStates.waiting_for_choose_campaign)


@router.callback_query(
    ResumeJobSeekerAskCampaignsStates.waiting_for_choose_campaign,
    F.data.startswith("campaign_request")
)
async def get_jobseeker_campaigns_ask(callback: CallbackQuery, state: FSMContext):

    campaign = callback.data.split(":")[-1].strip()

    campaign_label = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                campaign_label = button.text
                break

    payload = {
        "chat_id": callback.from_user.id,
        "campaign_channel": campaign
    }

    result = await create_campaign_channel_ask(payload)

    await callback.answer()

    # ✅ درخواست موفق
    if result["success"]:

        await callback.message.delete()

        await callback.message.answer(
            f"کارجوی گرامی کمپین «{campaign_label}» با موفقیت ثبت شد ✅"
        )

        await callback.message.answer(
            "کارجوی عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
            reply_markup=await get_jobseeker_main_menu()
        )

    # ✅ درخواست تکراری → دوباره کمپین‌ها را نشان بده
    elif result["type"] == "duplicate":

        await callback.message.edit_text(
            f"کارجوی گرامی شما قبلاً برای کمپین «{campaign_label}» درخواست ثبت کرده‌اید.\n"
            "لطفاً کمپین دیگری را انتخاب کنید:",
            reply_markup=await get_campaign_request_inline_keyboard()
        )

    # ✅ خطای دیگر
    else:

        await callback.message.edit_text(
            "در ثبت درخواست مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
            reply_markup=await get_campaign_request_inline_keyboard()
        )


@router.callback_query(
    F.data.startswith("back_ask_camagin_menu")
)
async def back_from_ask_campaign_to_jobseeker_main_menu(callback: CallbackQuery):

    await callback.answer()

    await callback.message.delete()

    await callback.message.answer(
        "کارجوی عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup=await get_jobseeker_main_menu()
    )
