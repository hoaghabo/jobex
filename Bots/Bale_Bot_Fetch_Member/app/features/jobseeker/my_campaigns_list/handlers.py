from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.infrastructure.backend.bot_user_api import get_user_status
from app.features.auth.permissions import (
    extract_menu_flags
)
from app.features.auth.states import RegisterStates

from .api import get_my_campaigns_list , format_campaign_requests
from app.features.jobseeker.jobseeker_main.keyboards import get_jobseeker_main_menu



router = Router()

@router.message(F.text == "لیست کمپین های من")
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
        "---------------------------لیست کمپین های من-----------------------",
        reply_markup=ReplyKeyboardRemove()
        )
    data = await get_my_campaigns_list(message.chat.id)

    text = format_campaign_requests(data)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="from_my_list_camagin_back_to_jobseekr_menu"
                )
            ]
        ]
    )

    await message.answer(
        text,
        reply_markup=keyboard
    )


@router.callback_query(
    F.data.startswith("from_my_list_camagin_back_to_jobseekr_menu")
)
async def back_from_ask_campaign_to_jobseeker_main_menu(callback: CallbackQuery):

    await callback.answer()

    await callback.message.delete()

    await callback.message.answer(
        "کارجوی عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup=await get_jobseeker_main_menu()
    )
