from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .formatter import get_choice_label,extract_phone_number
from app.infrastructure.backend.bot_user_api import get_user_status_by_chat_id
from app.infrastructure.backend.bot_user_api import (
    get_user_status,
    register_or_update_user,
)
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from .keyboards import (
    get_campaign_request_inline_keyboard,
    get_choices_items,
    get_city_inline_keyboard,
    get_degree_inline_keyboard,
    get_salary_range_inline_keyboard,
    get_work_enthusiasts_inline_keyboard,
    get_work_location_priority_inline_keyboard,
    get_birthday_day_inline_keyboard,
    get_birthday_month_inline_keyboard
)

from .states import ResumeJobSeekerCreateStates
from .formatter import normalize_digits
from .api import patch_jobseeker_profile_me

router = Router()


@router.message(F.text == "تکمیل رزومه آنلاین")
async def get_degree_handler(message: Message, state: FSMContext):
    await message.answer(
        "تکمیل رزومه شما \n"
        "لطفا مدرک تحصیلی خود را انتخاب کنید",
        reply_markup=await get_degree_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_degree
    )

@router.callback_query(F.data.startswith("degree:"))
async def get_year_birthday_handler(callback: CallbackQuery, state: FSMContext):
    degree = callback.data.split(":")[-1]

    await state.update_data(degree=degree)

    await callback.answer()

    await callback.message.edit_text(
        "لطفا سال تاریخ تولد خود را وارد کنید\n"
        "فرمت مناسب ورودی: ۱۳۸۴"
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_year_birthday)
    
    

@router.message(ResumeJobSeekerCreateStates.waiting_for_year_birthday, F.text)
async def get_month_birthday_handler(message: Message, state: FSMContext):
    year_birthday = message.text.strip()
    normalized_year = normalize_digits(year_birthday)

    if not normalized_year.isdigit() or len(normalized_year) != 4:
        await message.answer(
            "لطفا سال تاریخ تولد خود را به صورت معتبر وارد کنید.\n"
            "فرمت مناسب: ۱۳۸۴"
        )
        return

    year_birthday_int = int(normalized_year)

    if year_birthday_int < 1300 or year_birthday_int > 1405:
        await message.answer(
            "سال تولد وارد شده معتبر نیست.\n"
            "لطفا سالی مثل ۱۳۸۴ وارد کنید."
        )
        return

    await state.update_data(year_birthday=year_birthday_int)

    await message.answer(
        "لطفا ماه تاریخ تولد خود را انتخاب کنید:",
        reply_markup=await get_birthday_month_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_month_birthday
    )




@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_month_birthday,
    F.data.startswith("birthday_month:")
)
async def get_day_birthday_callback_handler(callback: CallbackQuery, state: FSMContext):
    month_birthday = callback.data.split(":")[-1]
    month_birthday_int = int(month_birthday)

    await state.update_data(month_birthday=month_birthday_int)
    await callback.answer()

    await callback.message.edit_text(
        "لطفا روز تاریخ تولد خود را انتخاب کنید:",
        reply_markup=await get_birthday_day_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_day_birthday
    )



@router.callback_query(F.data.startswith("birthday_day:"))
async def get_email_message_handler(callback: CallbackQuery, state: FSMContext):
    day_birthday = callback.data.split(":")[-1]

    day_birthday = callback.data.split(":")[-1]
    day_birthday_int = int(day_birthday)

    await state.update_data(day_birthday=day_birthday_int)
    await callback.answer()

    await callback.message.edit_text(
        "لطفا ایمیل خود را وارد کنید\n"
        "فرمت مناسب ورودی: info@jobex123.ir"
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_email)
    
    
    
import re

@router.message(ResumeJobSeekerCreateStates.waiting_for_email, F.text)
async def get_email_handler(message: Message, state: FSMContext):
    email = message.text.strip()

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    if not re.match(email_pattern, email):
        await message.answer(
            "لطفا ایمیل خود را به صورت معتبر وارد کنید.\n"
            "فرمت مناسب: info@jobex123.ir"
        )
        return

    await state.update_data(email=email)

    await message.answer(
        "لطفا محدوده جغرافیایی خود را انتخاب کنید:",
        reply_markup=await get_city_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_city
    )

    
@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_city,
    F.data.startswith("city:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split(":")[-1]

    await state.update_data(city=city)
    await callback.answer()

    await callback.message.edit_text(
        "لطفا علاقه‌مندی‌های شغلی خود را انتخاب کنید:",
        reply_markup=await get_work_enthusiasts_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_work_enthusiasts
    )



@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_work_enthusiasts,
    F.data.startswith("work_enthusiasts:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    work_enthusiasts = callback.data.split(":")[-1]

    await state.update_data(work_enthusiasts=work_enthusiasts)
    await callback.answer()

    await callback.message.edit_text(
        "لطفا حقوق درخواستی خود را انتخاب کنید:",
        reply_markup=await get_salary_range_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_salary_range
    )



@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_salary_range,
    F.data.startswith("salary_range:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    salary_range = callback.data.split(":")[-1]

    await state.update_data(salary_range=salary_range)
    await callback.answer()

    await callback.message.edit_text(
        "لطفا اولویت محل کار خود را انتخاب کنید:",
        reply_markup=await get_work_location_priority_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_work_location_priority
    )
    
    
@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_work_location_priority,
    F.data.startswith("work_location_priority:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    work_location_priority = callback.data.split(":")[-1]

    await state.update_data(work_location_priority=work_location_priority)
    await callback.answer()

    await callback.message.edit_text(
        "درخواست کمپین اطلاع رسانی خود را انتخاب کنید",
        reply_markup=await get_campaign_request_inline_keyboard()
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_campaign_request
    )


@router.callback_query(
    ResumeJobSeekerCreateStates.waiting_for_campaign_request,
    F.data.startswith("campaign_request:")
)
async def get_campaign_request_callback_handler(callback: CallbackQuery, state: FSMContext):
    campaign_request = callback.data.split(":")[-1]

    await state.update_data(campaign_request=campaign_request)
    await callback.answer()

    data = await state.get_data()

    degree_label = await get_choice_label(
        "degree",
        data.get("degree")
    )

    city_label = await get_choice_label(
        "city",
        data.get("city")
    )

    work_enthusiasts_label = await get_choice_label(
        "work_enthusiasts",
        data.get("work_enthusiasts")
    )

    salary_range_label = await get_choice_label(
        "salary_range",
        data.get("salary_range")
    )

    work_location_priority_label = await get_choice_label(
        "work_location_priority",
        data.get("work_location_priority")
    )

    campaign_request_label = await get_choice_label(
        "campaign_request",
        data.get("campaign_request")
    )

    summary_text = (
        "رزومه شما با موفقیت ثبت شد ✅\n\n"
        "خلاصه اطلاعات ثبت‌شده:\n\n"
        f"مدرک تحصیلی: {degree_label}\n"
        f"تاریخ تولد: {data.get('year_birthday')}/{data.get('month_birthday')}/{data.get('day_birthday')}\n"
        f"ایمیل: {data.get('email')}\n"
        f"محدوده جغرافیایی: {city_label}\n"
        f"علاقه‌مندی شغلی: {work_enthusiasts_label}\n"
        f"حقوق درخواستی: {salary_range_label}\n"
        f"اولویت محل کار: {work_location_priority_label}\n"
        f"درخواست کمپین اطلاع‌رسانی: {campaign_request_label}\n\n"
        "درخواست شما ثبت شد.\n"
        "همکاران ما به‌زودی با شما ارتباط می‌گیرند."
    )
    
    data = await state.get_data()
    user_status = await get_user_status_by_chat_id(callback.from_user.id)
    phone_number = extract_phone_number(user_status)

    if not phone_number:
        await callback.message.answer(
            "شماره موبایل شما پیدا نشد.\n"
            "لطفاً ابتدا ثبت‌نام/احراز شماره را انجام دهید و سپس دوباره رزومه را ثبت کنید."
        )
        return

    await callback.message.edit_text(summary_text)
    payload = {
        "phone_number": phone_number,
        "degree": data.get("degree"),
        "year_birthdate": data.get("year_birthday"),
        "month_birthdate": data.get("month_birthday"),
        "day_birthdate": data.get("day_birthday"),
        "email": data.get("email"),
        "city": data.get("city"),
        "work_enthusiasts": [data.get("work_enthusiasts")] if data.get("work_enthusiasts") else [],
        "salary_range": data.get("salary_range"),
        "work_location_priority": data.get("work_location_priority"),
        "campaign_request": [campaign_request] if campaign_request else [],
    }
    await patch_jobseeker_profile_me(payload)

    await state.clear()
