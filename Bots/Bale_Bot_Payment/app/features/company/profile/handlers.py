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
from .api import get_company_profile_status, patch_company_profile_me
from .keyboards import (
    get_city_inline_keyboard,
    get_organization_size_inline_keyboard,
)
from.states import CompanyProfileCreateStates
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "کارفرما")
async def choose_company_handler(message: Message, state: FSMContext):
    profile_status = None
    backend_response = None

    # 1. اول بررسی کن پروفایل کارفرما وجود دارد یا نه
    try:
        profile_status = await get_company_profile_status(message.chat.id)

    except Exception as e:
        print("Get company profile status error:", e)

        # اگر API شما برای نبودن پروفایل 404 می‌دهد،
        # اینجا باید فقط در حالت 404 اجازه ساخت پروفایل بدهی.
        # فعلاً چون نوع exception مشخص نیست، می‌رویم سراغ ساخت.
        profile_status = None

    # 2. اگر پروفایل وجود دارد
    if profile_status:
        menu_flags = extract_menu_flags(profile_status)
        menu_flags["is_bot_bale_member"] = True
        menu_flags["is_company_member"] = True

        if profile_status.get("is_registration_complete") is True:
            await message.answer(
                "پروفایل کارفرمایی شما قبلاً تکمیل شده است ✅",
                reply_markup=get_main_menu_keyboard(**menu_flags),
            )
            await state.clear()
            return

        await message.answer(
            "پروفایل کارفرمایی شما هنوز کامل نشده است.\n"
            "لطفاً برای ادامه مسیر پروفایل کارفرمایی خود را تکمیل نمایید.\n\n"
            "نام سازمان خود را وارد کنید."
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

    # 4. بعد از ساخت پروفایل، چون تازه ساخته شده و ناقص است، ببر برای تکمیل
    await message.answer(
        "پروفایل کارفرمایی شما ایجاد شد ✅\n"
        "لطفاً برای ادامه مسیر پروفایل خود را تکمیل نمایید.\n\n"
        "نام سازمان خود را وارد کنید."
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)



@router.message(CompanyProfileCreateStates.waiting_for_company_name, F.text)
async def get_company_name_handler(message: Message, state: FSMContext):
    company_name = message.text.strip()

    await state.update_data(company_name=company_name)

    await message.answer(
        "لطفا ایمیل خود را وارد کنید\n"
        "فرمت مناسب ورودی: info@jobex123.ir"
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_email)

    
    
@router.message(CompanyProfileCreateStates.waiting_for_email, F.text)
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
        "لطفا ابعاد سازمان خود را انتخاب کنید:",
        reply_markup=await get_organization_size_inline_keyboard()
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_organization_size)

@router.callback_query(
    CompanyProfileCreateStates.waiting_for_organization_size,
    F.data.startswith("organization_size:")
)
async def get_city_callback_handler(callback: CallbackQuery, state: FSMContext):
    organization_size = callback.data.split(":")[-1]

    await state.update_data(organization_size=organization_size)

    await callback.message.edit_text(
        "لطفا محدوده جغرافیایی خود را انتخاب کنید:",
        reply_markup=await get_city_inline_keyboard()
    )


    await state.set_state(
        CompanyProfileCreateStates.waiting_for_city
    )


@router.callback_query(F.data.startswith("city:"))
async def get_year_birthday_handler(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split(":")[-1]

    await state.update_data(city=city)

    await callback.answer()

    await callback.message.edit_text(
        "لطفا صنعت/حوزه خود را وارد کنید\n"
        "فرمت مناسب ورودی: دیجیتال و فناوری"
    )

    await state.set_state(
        CompanyProfileCreateStates.waiting_for_industry)




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
