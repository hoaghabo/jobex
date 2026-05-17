from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .formatter import get_choice_label,extract_phone_number
from app.infrastructure.backend.bot_user_api import get_user_status_by_chat_id
from app.infrastructure.backend.bot_user_api import (
    get_user_status,
    register_or_update_user,
)
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from app.infrastructure.backend.bot_user_api import create_company_profile, create_jobseeker_profile
from .keyboards import (
update_jobseeker_resume_keyboards,
get_degree_inline_keyboard,
get_work_enthusiasts_inline_keyboard,
get_salary_range_inline_keyboard,
get_work_location_priority_inline_keyboard
)

from app.features.auth.permissions import (
    extract_menu_flags
)

from app.features.auth.states import RegisterStates
from app.features.jobseeker.jobseeker_main.keyboards import get_jobseeker_main_menu
from .states import ResumeJobSeekerUpdateStates
from .formatter import format_jobseeker_profile_text
from .api import patch_jobseeker_profile_me , get_jobseeker_profile_me

router = Router()

@router.message(F.text == "بروزرسانی رزومه")
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


    jobseeker_payload = {
        "chat_id" : message.chat.id
    }

    jobseeker_profile = await get_jobseeker_profile_me(jobseeker_payload)
    
    profile_text = format_jobseeker_profile_text(jobseeker_profile)
    remove_msg = await message.answer(
        "---------------------------بروزرسانی رزومه-------------------------",
        reply_markup=ReplyKeyboardRemove()
    )

    await message.answer(
        profile_text,
        reply_markup=await update_jobseeker_resume_keyboards()
    )


@router.callback_query(F.data.startswith("back_update_resume_menu"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery):
    jobseeker_payload = {
        "chat_id": callback.message.chat.id
    }
    jobseeker_profile = await get_jobseeker_profile_me(jobseeker_payload)
    
    profile_text = format_jobseeker_profile_text(jobseeker_profile)

    await callback.message.edit_text(
        profile_text,
        reply_markup=await update_jobseeker_resume_keyboards()
    )





@router.callback_query(F.data.startswith("update_degree"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    await callback.message.edit_text(
        "لطفا مدرک تحصیلی خود را انتخاب کنید:",
        reply_markup=await get_degree_inline_keyboard()
    )
    await callback.answer()
    await state.set_state(ResumeJobSeekerUpdateStates.waiting_for_degree)



@router.callback_query(ResumeJobSeekerUpdateStates.waiting_for_degree , F.data.startswith("degree:"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    degree = callback.data.split(":")[-1]
    update_resume_payload = {
        "chat_id": callback.message.chat.id,
        "degree": degree
    }
    await patch_jobseeker_profile_me(update_resume_payload)
    jobseeker_profile = await get_jobseeker_profile_me(update_resume_payload)
    profile_text = format_jobseeker_profile_text(jobseeker_profile)

    await callback.message.edit_text(
        profile_text ,
        reply_markup=await update_jobseeker_resume_keyboards()
    )
    await state.clear()



@router.callback_query(F.data.startswith("update_work_enthusiasts"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    await callback.message.edit_text(
        "لطفا علاقه مندی شغلی خود را انتخاب کنید:",
        reply_markup=await get_work_enthusiasts_inline_keyboard()
    )
    await callback.answer()
    await state.set_state(ResumeJobSeekerUpdateStates.waiting_for_work_enthusiasts)



@router.callback_query(ResumeJobSeekerUpdateStates.waiting_for_work_enthusiasts , F.data.startswith("work_enthusiasts:"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    work_enthusiasts = callback.data.split(":")[-1]
    update_resume_payload = {
        "chat_id": callback.message.chat.id,
        "work_enthusiasts": [work_enthusiasts]
    }
    await patch_jobseeker_profile_me(update_resume_payload)
    jobseeker_profile = await get_jobseeker_profile_me(update_resume_payload)
    profile_text = format_jobseeker_profile_text(jobseeker_profile)

    await callback.message.edit_text(
        profile_text,
        reply_markup=await update_jobseeker_resume_keyboards()
    )
    await state.clear()



    
@router.callback_query(F.data.startswith("update_salary_range"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    await callback.message.edit_text(
        "لطفا بازه حقوق مد نظر خود را انتخاب کنید:",
        reply_markup=await get_salary_range_inline_keyboard()
    )
    await callback.answer()
    await state.set_state(ResumeJobSeekerUpdateStates.waiting_for_salary_range)



@router.callback_query(ResumeJobSeekerUpdateStates.waiting_for_salary_range , F.data.startswith("salary_range:"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    salary_range = callback.data.split(":")[-1]
    update_resume_payload = {
        "chat_id": callback.message.chat.id,
        "salary_range": salary_range
    }
    await patch_jobseeker_profile_me(update_resume_payload)
    jobseeker_profile = await get_jobseeker_profile_me(update_resume_payload)
    profile_text = format_jobseeker_profile_text(jobseeker_profile)

    await callback.message.edit_text(
        profile_text,
        reply_markup=await update_jobseeker_resume_keyboards()
    )
    await state.clear()



@router.callback_query(F.data.startswith("update_work_location_priority"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    await callback.message.edit_text(
        "لطفا محدوده جغرافیایی کاری خود را انتخاب کنید:",
        reply_markup=await get_work_location_priority_inline_keyboard()
    )
    await callback.answer()
    await state.set_state(ResumeJobSeekerUpdateStates.waiting_for_work_location_priority)



@router.callback_query(ResumeJobSeekerUpdateStates.waiting_for_work_location_priority , F.data.startswith("work_location_priority:"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery , state : FSMContext):
    work_location_priority = callback.data.split(":")[-1]
    update_resume_payload = {
        "chat_id": callback.message.chat.id,
        "work_location_priority": work_location_priority
    }
    await patch_jobseeker_profile_me(update_resume_payload)
    jobseeker_profile = await get_jobseeker_profile_me(update_resume_payload)
    profile_text = format_jobseeker_profile_text(jobseeker_profile)

    await callback.message.edit_text(
        profile_text,
        reply_markup=await update_jobseeker_resume_keyboards()
    )
    await state.clear()




@router.callback_query(F.data.startswith("back_main_menu_jobseeker"))
async def from_update_resume_back_to_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "کارجوی عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup=await get_jobseeker_main_menu()
    )
    await callback.answer()
