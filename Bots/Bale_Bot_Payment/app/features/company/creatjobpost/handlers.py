from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .formatter import get_choice_label,extract_phone_number, normalize_website
import re
from app.infrastructure.backend.bot_user_api import get_user_status_by_chat_id
from app.infrastructure.backend.bot_user_api import (
    get_user_status,
    register_or_update_user,
)
from app.infrastructure.backend.bot_user_api import create_company_profile
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from app.features.auth.permissions import extract_menu_flags
from app.features.company.profile.api import get_company_profile_status, patch_company_profile_me
from .keyboards import (
    get_attendance_type_inline_keyboard,
    get_cooperation_type_inline_keyboard,
    get_degree_inline_keyboard,
    get_job_title_inline_keyboard,
    get_minimum_work_experiencee_inline_keyboard,
    get_working_days_inline_keyboard,
    get_working_hours_inline_keyboard,
)
from.states import CompanyJobPostCreateStates
from app.features.company.profile.states import CompanyProfileCreateStates
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "ثبت نیازمندی جدید")
async def choose_company_handler(message: Message, state: FSMContext):
    profile_status = None
    backend_response = None

    # 1. بررسی وجود پروفایل کارفرما
    try:
        profile_status = await get_company_profile_status(message.chat.id)

    except Exception as e:
        print("Get company profile status error:", e)

        # اگر API برای نبودن پروفایل 404 می‌دهد،
        # بهتر است فقط در حالت 404 پروفایل بسازی.
        # فعلاً طبق منطق قبلی، اگر خطا خورد فرض می‌کنیم پروفایل وجود ندارد.
        profile_status = None

    # 2. اگر پروفایل کارفرمایی وجود دارد
    if profile_status:
        menu_flags = extract_menu_flags(profile_status)
        menu_flags["is_bot_bale_member"] = True
        menu_flags["is_company_member"] = True

        # اگر پروفایل کامل است، اجازه ثبت آگهی بده
        if profile_status.get("is_registration_complete") is True:
            await message.answer(
                "برای ثبت نیازمندی جدید، لطفاً عنوان شغلی را وارد کنید.",
                reply_markup=await get_job_title_inline_keyboard()
                
            )

            await state.set_state(CompanyJobPostCreateStates.waiting_for_job_title)
            return

        # اگر پروفایل ناقص است، اول تکمیل پروفایل
        await message.answer(
            "برای ثبت نیازمندی جدید، ابتدا باید پروفایل کارفرمایی خود را تکمیل کنید.\n\n"
            "لطفاً نام سازمان خود را وارد کنید."
        )
        await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)
        return

    # 3. اگر پروفایل وجود ندارد، بساز
    try:
        backend_response = await create_company_profile(message)

    except Exception as e:
        print("Create company profile error:", e)
        await message.answer(
            "فعلاً امکان ساخت پروفایل کارفرما وجود ندارد. لطفاً دوباره تلاش کنید."
        )
        return

    menu_flags = extract_menu_flags(backend_response)
    menu_flags["is_bot_bale_member"] = True
    menu_flags["is_company_member"] = True

    # 4. بعد از ساخت پروفایل، چون ناقص است، اول تکمیل پروفایل
    await message.answer(
        "پروفایل کارفرمایی شما ایجاد شد ✅\n"
        "برای ثبت نیازمندی جدید، ابتدا باید پروفایل خود را تکمیل کنید.\n\n"
        "لطفاً نام سازمان خود را وارد کنید."
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)

    
    
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_job_title,
    F.data.startswith("job_title:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    cooperation_type = callback.data.split(":")[-1]

    await state.update_data(cooperation_type=cooperation_type)

    await callback.message.edit_text(
        "لطفا نوع همکاری را انتخاب کنید:",
        reply_markup=await get_cooperation_type_inline_keyboard()
    )

    await state.set_state(CompanyJobPostCreateStates.waiting_for_cooperation_type)




@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_cooperation_type,
    F.data.startswith("cooperation_type:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    cooperation_type = callback.data.split(":")[-1]

    await state.update_data(cooperation_type=cooperation_type)

    await callback.message.edit_text(
        "لطفا مدرک مورد نظر را انتخاب کنید:",
        reply_markup=await get_degree_inline_keyboard()
    )


    await state.set_state(
        CompanyJobPostCreateStates.waiting_for_degree
    )




@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_degree,
    F.data.startswith("jobpost_degree:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    degree = callback.data.split(":")[-1]

    await state.update_data(degree=degree)

    await callback.message.edit_text(
        "لطفا حداقل سابقه کاری مورد نظر را انتخاب کنید:",
        reply_markup=await get_minimum_work_experiencee_inline_keyboard()
    )


    await state.set_state(
        CompanyJobPostCreateStates.waiting_for_minimum_work_experience
    )





@router.message(CompanyProfileCreateStates.waiting_for_industry, F.text)
async def get_month_birthday_handler(message: Message, state: FSMContext):
    industry = message.text.strip()
    
    await state.update_data(industry=industry)
    
    await message.answer(
        "لطفا آدرس کامل سازمان خود را وارد کنید\n"
        "فرمت مناسب ورودی:  تهران - تجریش - خیابان رضایی - کوچه لاله - پلاک ۱۲ - زنگ سوم - طبقه چهارم - واحد ۲ "
    )

    await state.set_state(
        CompanyProfileCreateStates.waiting_for_full_address
    )



@router.message(CompanyProfileCreateStates.waiting_for_full_address, F.text)
async def get_month_birthday_handler(message: Message, state: FSMContext):
    full_address = message.text.strip()
    
    await state.update_data(full_address=full_address)
    
    await message.answer(
        "لطفا آدرس وبسایت سازمان خود را وارد کنید\n"
        "فرمت مناسب ورودی:  jobex123.ir "
    )

    await state.set_state(
        CompanyProfileCreateStates.waiting_for_website
    )



@router.message(CompanyProfileCreateStates.waiting_for_website, F.text)
async def get_month_birthday_handler(message: Message, state: FSMContext):
    website = message.text.strip()
    
    await state.update_data(website=website)
    
    await message.answer(
        "لطفا تلفن ثابت سازمان خود را وارد کنید\n"
        "فرمت مناسب ورودی:  ۰۲۱-۴۴۳۳۲۲۵۵ "
    )

    await state.set_state(
        CompanyProfileCreateStates.waiting_for_landline_phone
    )



@router.message(CompanyProfileCreateStates.waiting_for_landline_phone, F.text)
async def get_landline_phone_handler(message: Message, state: FSMContext):
    landline_phone = message.text.strip()

    await state.update_data(landline_phone=landline_phone)
    data = await state.get_data()

    organization_size_label = await get_choice_label(
        "organization_size",
        data.get("organization_size")
    )
    city_label = await get_choice_label(
        "city",
        data.get("city")
    )

    user_status = await get_user_status_by_chat_id(message.from_user.id)
    phone_number = extract_phone_number(user_status)

    if not phone_number:
        await message.answer(
            "شماره موبایل شما پیدا نشد.\n"
            "لطفاً ابتدا ثبت‌نام/احراز شماره را انجام دهید و سپس دوباره پروفایل کارفرما را تکمیل کنید."
        )
        return

    payload = {
        "phone_number": phone_number,
        "company_name": data.get("company_name"),
        "email": data.get("email"),
        "organization_size": data.get("organization_size"),
        "city": data.get("city"),
        "industry": data.get("industry"),
        "full_address": data.get("full_address"),
        "website" : normalize_website(data.get("website", "")),
        "landline_phone": landline_phone,
    }

    try:
        await patch_company_profile_me(payload)

        profile_status = await get_company_profile_status(chat_id=message.from_user.id)
        is_complete = profile_status.get("is_registration_complete", False)

        summary_text = (
            "پروفایل کارفرمایی شما با موفقیت ثبت شد ✅\n\n"
            "خلاصه اطلاعات ثبت‌شده:\n\n"
            f"نام سازمان: {data.get('company_name')}\n"
            f"ایمیل: {data.get('email')}\n"
            f"ابعاد سازمان: {organization_size_label}\n"
            f"محدوده جغرافیایی: {city_label}\n"
            f"صنعت/حوزه: {data.get('industry')}\n"
            f"آدرس کامل: {data.get('full_address')}\n"
            f"وب‌سایت: {data.get('website')}\n"
            f"تلفن ثابت: {landline_phone}\n"
        )

        if profile_status:
            menu_flags = extract_menu_flags(profile_status)
            menu_flags["is_bot_bale_member"] = True
            menu_flags["is_company_member"] = True

            if profile_status.get("is_registration_complete") is True:
                await message.answer(
                    "پروفایل کارفرمایی شما تکمیل شده است ✅",
                    reply_markup=get_main_menu_keyboard(**menu_flags),
                )
                await state.clear()
        else:
            await message.answer(
                summary_text + "\nاطلاعات ذخیره شد، اما پروفایل شرکت هنوز کامل نشده است."
            )

        await state.clear()

    except Exception as e:
        await message.answer(
            "در ثبت اطلاعات پروفایل شرکت خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        # اگر لاگر داری:
        logger.exception("Company profile patch error: %s", e)
