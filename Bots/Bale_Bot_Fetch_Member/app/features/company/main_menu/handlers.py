from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.infrastructure.backend.bot_user_api import get_user_status
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from app.infrastructure.backend.bot_user_api import create_jobseeker_profile
from .keyboards import (
    get_company_main_menu
)
from app.features.auth.permissions import (
    extract_menu_flags
)

from app.features.auth.states import RegisterStates






router = Router()

@router.message(F.text == "کارفرما")
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

    
    await message.answer(
        "کارفرمای عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup = await get_company_main_menu()
    )