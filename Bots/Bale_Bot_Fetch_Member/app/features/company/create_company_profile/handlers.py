from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
import re
from contextlib import suppress
from app.features.auth.states import RegisterStates

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
from .api import get_company_profile_status, post_company_profile_me
from .keyboards import (
    get_city_inline_keyboard,
    get_organization_size_inline_keyboard,
    get_membership_role_inline_keyboard,
    build_choices_inline_keyboard,
)
from app.features.company.main_menu.keyboards import get_company_main_menu
from .api import get_role_membership_channels
from.states import CompanyProfileCreateStates
import logging

logger = logging.getLogger(__name__)
router = Router()


    
@router.message(F.text == "ثبت شرکت جدید")
@router.callback_query(F.data.startswith("create_company_From_my_company_list"))
@router.callback_query(F.data.startswith("create_company_from_jobpost_request"))
async def start_create_company_handler(event: Message | CallbackQuery, state: FSMContext):
    # -------------------------------------------------
    # 0. تشخیص نوع ورودی
    # -------------------------------------------------
    if isinstance(event, CallbackQuery):
        await event.answer()

        try:
            await event.message.delete()
        except Exception as e:
            print("Delete message error:", e)

        message = event.message
        chat_id = event.from_user.id
    else:
        message = event
        chat_id = event.from_user.id

    # -------------------------------------------------
    # 1. گرفتن وضعیت کلی کاربر
    # -------------------------------------------------
    try:
        status_response = await get_user_status_by_chat_id(chat_id)
    except Exception as e:
        print("Get user status error:", e)
        await message.answer(
            "خطا در دریافت اطلاعات کاربر. لطفاً دوباره تلاش کنید."
        )
        return

    menu_flags = extract_menu_flags(status_response)
    print(f"===================>>>> {menu_flags}")

    is_registered = menu_flags.get("is_bot_bale_member", False)

    # -------------------------------------------------
    # حالت اول: کاربر اصلاً ثبت‌نام نکرده
    # -------------------------------------------------
    if not is_registered:
        await message.answer(
            "ابتدا باید ثبت‌نام کنید.\n"
            "لطفاً نام و نام خانوادگی خود را وارد کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegisterStates.waiting_for_first_name)
        return

    # -------------------------------------------------
    # حالت دوم: کاربر ثبت‌نام کرده ولی پروفایل کارفرمایی ندارد
    # -------------------------------------------------
    msg = await message.answer(
        "-------------------ثبت شرکت جدید------------\n"
        "لطفاً برای شروع، نام سازمان خود را وارد کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )

    await msg.edit_reply_markup(
        reply_markup=await build_choices_inline_keyboard(callback_prefix="company_name")
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)
    return




@router.callback_query(
    CompanyProfileCreateStates.waiting_for_company_name,
    F.data.endswith(":back")
)
async def back_to_company_main_menu(callback: CallbackQuery, state: FSMContext):

    await callback.answer()

    await callback.message.delete()

    await callback.message.answer(
        "کارفرمای عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup= await get_company_main_menu()
    )

    await state.clear()






@router.message(CompanyProfileCreateStates.waiting_for_company_name, F.text)
async def get_company_name_handler(message: Message, state: FSMContext):
    company_name = message.text.strip()

    await state.update_data(company_name=company_name)
    
    

    await message.answer(
        "لطفاً نقش خود در سازمان را وارد کنید.\n"
        "مثال: مدیرعامل، منابع انسانی، مدیر فنی، کارشناس استخدام",
         reply_markup = await get_membership_role_inline_keyboard()
    )


    await state.set_state(CompanyProfileCreateStates.waiting_for_company_role)

    
    

@router.callback_query(
    CompanyProfileCreateStates.waiting_for_company_role,
    F.data.startswith("membership_role:")
)
async def get_email_handler(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[-1]
    print(f"=================ROLE========== .>>>>>>> {role}")
    await state.update_data(role=role)

    await callback.message.edit_text(
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


@router.callback_query(CompanyProfileCreateStates.waiting_for_city , F.data.startswith("city:"))
async def get_year_birthday_handler(callback: CallbackQuery, state: FSMContext):
    with suppress(TelegramAPIError):
        await callback.answer()
    print("================>> I Am uPDATEEEEEEEEEEEEEEE")

    city = callback.data.split(":")[-1]
    await state.update_data(city=city)

    await callback.message.edit_text(
        "لطفا صنعت/حوزه خود را وارد کنید\n"
        "فرمت مناسب ورودی: دیجیتال و فناوری"
    )

    await state.set_state(CompanyProfileCreateStates.waiting_for_industry)



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

URL_REGEX = re.compile(
    r"^(https?:\/\/)?([\w\-]+\.)+[\w\-]{2,}(\/[\w\-._~:/?#[\]@!$&'()*+,;=]*)?$"
)


@router.message(CompanyProfileCreateStates.waiting_for_website, F.text)
async def get_month_birthday_handler(message: Message, state: FSMContext):
    
    website = message.text.strip()

    if not URL_REGEX.match(website):
        await message.answer(
            "❌ آدرس وبسایت معتبر نیست.\n"
            "نمونه صحیح:\n"
            "example.com\n"
            "https://example.com"
        )
        return

    # اگر scheme نداشت اضافه می‌کنیم
    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"

    await state.update_data(website=website)

    await message.answer(
        "لطفا تلفن ثابت سازمان خود را وارد کنید\n"
        "فرمت مناسب ورودی: ۰۲۱-۴۴۳۳۲۲۵۵"
    )

    await state.set_state(
        CompanyProfileCreateStates.waiting_for_landline_phone
    )


import re

LANDLINE_REGEX = re.compile(r"^0\d{2,3}\d{7,8}$")


@router.message(CompanyProfileCreateStates.waiting_for_landline_phone, F.text)
async def get_landline_phone_handler(message: Message, state: FSMContext):

    landline_phone = message.text.strip()

    # validate landline
    if not LANDLINE_REGEX.match(landline_phone):
        await message.answer(
            "❌ فرمت تلفن ثابت صحیح نیست.\n"
            "نمونه صحیح:\n"
            "02144332255"
        )
        return

    await state.update_data(landline_phone=landline_phone)
    data = await state.get_data()

    organization_size_label = await get_choice_label(
        "organization_size",
        data.get("organization_size")
    )

    website = normalize_website(data.get("website", ""))

    user_status = await get_user_status_by_chat_id(message.from_user.id)
    phone_number = extract_phone_number(user_status)

    if not phone_number:
        await message.answer(
            "شماره موبایل شما پیدا نشد.\n"
            "لطفاً ابتدا ثبت‌نام/احراز شماره را انجام دهید و سپس دوباره پروفایل کارفرما را تکمیل کنید."
        )
        return

    payload = {
        "chat_id": message.from_user.id,
        "company_name": data.get("company_name"),
        "organization_size": data.get("organization_size"),
        "city": data.get("city"),
        "industry": data.get("industry"),
        "full_address": data.get("full_address"),
        "website": website,
        "landline_phone": landline_phone,
        "role": data.get("role"),
    }

    from app.infrastructure.backend.client import BackendAPIError

    try:

        response = await post_company_profile_me(payload=payload)

        summary_text = (
            "✅ پروفایل کارفرمایی شما با موفقیت ثبت شد\n\n"
            "خلاصه اطلاعات ثبت‌شده:\n\n"
            f"نام سازمان: {data.get('company_name')}\n"
            f"نقش شما: {data.get("role")}\n"
            f"ابعاد سازمان: {organization_size_label}\n"
            f"محدوده جغرافیایی: {data.get("city")}\n"
            f"صنعت/حوزه: {data.get('industry')}\n"
            f"آدرس کامل: {data.get('full_address')}\n"
            f"وب‌سایت: {website}\n"
            f"تلفن ثابت: {landline_phone}"
        )

        await message.answer(summary_text)

        await message.answer(
            "اکنون می‌توانید از امکانات پنل کارفرمایان استفاده کنید.",
            reply_markup=await get_company_main_menu()
        )

        await state.clear()


    except BackendAPIError as e:

        logger.exception("Company profile create error: %s", e)

        error_message = None

        if isinstance(e.body, dict):

            if "company_name" in e.body:
                error_message = e.body["company_name"]

            elif "role" in e.body:
                error_message = e.body["role"]

        await message.answer(
            error_message or "❌ در ثبت اطلاعات پروفایل شرکت خطایی رخ داد.\nلطفاً دوباره تلاش کنید.",
            reply_markup=await get_company_main_menu()
        )


    except Exception as e:

        logger.exception("Unexpected error: %s", e)

        await message.answer(
            "❌ خطای غیرمنتظره‌ای رخ داد.\nلطفاً چند دقیقه بعد دوباره تلاش کنید.",
            reply_markup=await get_company_main_menu()
        )








