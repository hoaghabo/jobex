from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import traceback

from app.features.auth.permissions import (
    is_admin_user,
    is_registered_user,
    extract_menu_flags,
)
from app.features.auth.states import RegisterStates
from app.infrastructure.backend.bot_user_api import (
    get_user_status
)
from app.infrastructure.backend.client import BackendAPIError
from .keyboards import (
    get_account_list_choices,
    build_choices_inline_keyboard,
    build_city_inline_keyboard,
    get_birthday_day_inline_keyboard,
    get_birthday_month_inline_keyboard
    )
from app.shared.keyboards.contact import get_contact_keyboard
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from .service import registered_or_update_account , registered_or_update_balebotprofile


router = Router()


@router.message(CommandStart())
@router.message(F.text == "عضویت در بات")
async def start_handler(message: Message, state: FSMContext):
    await state.clear()

    try:
        status_response = await get_user_status(message)
    except Exception as e:
        print("Get user status error:", e)
        traceback.print_exc()

        await message.answer(
            "فعلاً امکان بررسی وضعیت شما وجود ندارد. لطفاً چند دقیقه دیگر دوباره تلاش کنید."
        )
        return

    if is_registered_user(status_response):
        menu_flags = extract_menu_flags(status_response)

        await message.answer(
            "خوش آمدید 👋\n"
            "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=get_main_menu_keyboard(**menu_flags , state = "starter"),
        )
        return

    await message.answer(
        "برای استفاده از ربات ابتدا باید ثبت‌نام کنید.\n"
        "لطفاً نام خود را وارد کنید."
    )
    await state.set_state(RegisterStates.waiting_for_first_name)
    

@router.message(RegisterStates.waiting_for_first_name, CommandStart())
@router.message(RegisterStates.waiting_for_first_name, F.text == "عضویت در بات")
async def get_start_handler_agian_handler(message: Message, state: FSMContext):
    await message.answer(
        "برای استفاده از ربات ابتدا باید ثبت‌نام کنید.\n"
        "لطفاً نام خود را وارد کنید."
    )
    await state.set_state(RegisterStates.waiting_for_first_name)



@router.message(RegisterStates.waiting_for_first_name, F.text)
async def get_first_name_handler(message: Message, state: FSMContext):
    first_name = message.text.strip()

    if len(first_name) < 3:
        await message.answer("لطفاً نام خود را کامل وارد کنید.")
        return

    await state.update_data(first_name=first_name)

    await message.answer(
        "لطفاً نام خانوادگی خود را وارد کنید."
    )
    await state.set_state(RegisterStates.waiting_for_last_name)
    

@router.message(RegisterStates.waiting_for_last_name, F.text)
async def get_last_name_handler(message: Message, state: FSMContext):
    last_name = message.text.strip()

    if len(last_name) < 3:
        await message.answer("لطفاً نام خانوادگی خود را کامل وارد کنید.")
        return

    await state.update_data(last_name=last_name)

    await message.answer(
        "ممنون 🌱\n"
        "حالا لطفاً شماره موبایل خود را با دکمه زیر ارسال کنید.",
        reply_markup=get_contact_keyboard(),
    )

    await state.set_state(RegisterStates.waiting_for_phone_number)
    
    
@router.message(RegisterStates.waiting_for_phone_number, F.contact)
async def get_phone_contact_handler(message: Message, state: FSMContext):
    contact = message.contact

    if not contact or not contact.phone_number:
        await message.answer(
            "شماره موبایل دریافت نشد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_contact_keyboard(),
        )
        return

    if message.from_user and contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(
            "لطفاً فقط شماره موبایل متعلق به خودتان را ارسال کنید.",
            reply_markup=get_contact_keyboard(),
        )
        return

    await state.update_data(phone_number=contact.phone_number)
    await message.answer("لطفا ایمیل خود را وارد کنید.")
    await state.set_state(RegisterStates.waiting_for_email)



@router.message(RegisterStates.waiting_for_phone_number, F.text)
async def get_phone_number_again_handler(message:Message):
        await message.answer(
        "لطفاً فقط شماره موبایل متعلق به خودتان را ارسال کنید.",
        reply_markup=get_contact_keyboard(),
    )

@router.message(RegisterStates.waiting_for_email, F.text)
async def get_email_handler(message: Message, state: FSMContext):
    email_address = message.text.strip()

    if email_address.count("@") != 1:
        await message.answer("لطفا ایمیل معتبر ارسال کنید.")
        return

    local_part, domain_part = email_address.split("@")

    if len(local_part) < 3:
        await message.answer("بخش قبل از @ باید حداقل ۳ کاراکتر باشد.")
        return

    if "." not in domain_part:
        await message.answer("دامنه ایمیل معتبر نیست.")
        return

    if len(domain_part.split(".")[0]) < 2:
        await message.answer("دامنه ایمیل معتبر نیست.")
        return

    await state.update_data(email=email_address)
    await message.answer(
        "لطفا جنسیت خود را انتخاب کنید",
        reply_markup= await build_choices_inline_keyboard("gender_choices", "gender:"),
    )
    await state.set_state(RegisterStates.waiting_for_gender)
    
    
@router.message(RegisterStates.waiting_for_gender,F.text)
async def get_gender_again_handler(message:Message):
        await message.answer(
        "لطفا جنسیت خود را از طریق دکمه های تعریف شده انتخاب کنید",
        reply_markup= await build_choices_inline_keyboard("gender_choices", "gender:"),
    )
    

@router.callback_query(RegisterStates.waiting_for_gender,F.data.startswith("gender:"))
async def get_gender_handlers(callback : CallbackQuery , state : FSMContext):
    gender_type = callback.data.split(":")[-1]
    await state.update_data(gender = gender_type)
    await callback.message.edit_text(
        "لطفا شهر یا استان خود را انتخاب کنید:",
        reply_markup = await build_city_inline_keyboard()
    )
    await state.set_state(RegisterStates.waiting_for_city)
     
 
@router.message(RegisterStates.waiting_for_city,F.text)
async def get_city_again_handler(message:Message):
        await message.answer(
        "لطفا شهر یا استان خود را از طریق دکمه های تعریف شده انتخاب کنید",
        reply_markup = await build_city_inline_keyboard()
    )
        
@router.callback_query(RegisterStates.waiting_for_city , F.data.startswith("city:"))
async def get_city_handler(callback:CallbackQuery, state: FSMContext):
    city = callback.data.split(":")[-1]
    await state.update_data(city=city)
    await callback.message.edit_text(
        "لطفا روز تاریخ تولد خود را از گزینه های زیر انتخاب کنید",
        reply_markup = await get_birthday_day_inline_keyboard(),
    )
    await state.set_state(RegisterStates.waiting_for_day_birthdate)
    

@router.message(RegisterStates.waiting_for_day_birthdate,F.text)
async def get_day_birthdate_again_handler(message:Message):
        await message.answer(
        "لطفا روز تاریخ تولد خود را از طریق دکمه های تعریف شده انتخاب کنید",
        reply_markup = await get_birthday_day_inline_keyboard(),
    )



@router.callback_query(RegisterStates.waiting_for_day_birthdate , F.data.startswith("birthdate_day"))
async def get_day_birthdate(callback : CallbackQuery , state: FSMContext):
    day_birthdate = callback.data.split(":")[-1]
    await state.update_data(day_birthdate = day_birthdate)
    await callback.message.edit_text(
        "لطفا ماه تاریخ تولد خود را انتخاب کنید",
        reply_markup = await get_birthday_month_inline_keyboard()
    )
    await state.set_state(RegisterStates.waiting_for_month_birthdate)



@router.message(RegisterStates.waiting_for_month_birthdate,F.text)
async def get_month_birthdate_again_handler(message:Message):
        await message.answer(
        "لطفا ماه تاریخ تولد خود را از طریق دکمه های تعریف شده انتخاب کنید",
        reply_markup = await get_birthday_month_inline_keyboard(),
    )




@router.callback_query(RegisterStates.waiting_for_month_birthdate , F.data.startswith("birthdate_month"))
async def get_month_birthdate(callback : CallbackQuery , state: FSMContext):
    month_birthdate = callback.data.split(":")[-1]
    await state.update_data(month_birthdate = month_birthdate)
    await callback.message.edit_text(
        "(فرمت صحیح: 1384) لطفا سال تاریخ تولد خود را وارد کنید"
    )
    await state.set_state(RegisterStates.waiting_for_year_birthdate)
    


@router.message(RegisterStates.waiting_for_year_birthdate, F.text)
async def get_year_birthdate_handler(message: Message, state: FSMContext):
    year_birthdate = message.text.strip()

    if len(year_birthdate) != 4 or not year_birthdate.isdigit():
        await message.answer(
            "لطفا سال تاریخ تولد را به فرمت 4 رقمی مثل 1384 وارد کنید."
        )
        return

    await state.update_data(year_birthdate=year_birthdate)
    data = await state.get_data()
    print(f"data ========= {data}")

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    email = data.get("email")
    gender = data.get("gender")
    city = data.get("city")
    day_birthdate = data.get("day_birthdate")
    month_birthdate = data.get("month_birthdate")
    year_birthdate = data.get("year_birthdate")

    user_id = message.from_user.id if message.from_user else None
    
    account_register_payload = {
    "first_name": first_name,
    "last_name": last_name,
    "phone_number": phone_number,
    "email": email,
    "gender": gender,
    "city": city,
    "day_birthdate": day_birthdate,
    "month_birthdate": month_birthdate,
    "year_birthdate": year_birthdate,
}


    try:
        backend_response = await registered_or_update_account(account_register_payload)
        print("backend_response =", backend_response)

        bale_profile_payload = {
            "chat_id": message.chat.id if message.chat else None,
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "phone_number": phone_number,
            "profile_first_name": message.from_user.first_name if message.from_user and message.from_user.first_name else "",
            "profile_last_name": message.from_user.last_name if message.from_user and message.from_user.last_name else "",
            "registered_full_name": f"{first_name or ''} {last_name or ''}".strip(),
            "bale_bot_name": "fetch_data",
            "is_synced": True,
        }

        bale_profile_response = await registered_or_update_balebotprofile(
            bale_profile_payload
        )

        print("bale_profile_response =", bale_profile_response)

    except BackendAPIError as e:
        print("Backend API Error:", e)

        await message.answer(
            "ثبت‌نام شما فعلاً انجام نشد. ارتباط با سرور برقرار نشد.\n"
            "لطفاً چند دقیقه دیگر دوباره تلاش کنید."
        )
        return

    except Exception as e:
        print("Unexpected Error:", e)
        traceback.print_exc()

        await message.answer(
            "خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید."
        )
        return

    await state.set_state(RegisterStates.choose_type_of_customer)
    status_response = await get_user_status(message)
    menu_flags = extract_menu_flags(status_response)
    await message.answer(
        "ثبت‌نام اولیه شما با موفقیت انجام شد ✅\n\n"
        f"نام: {first_name or '-'}\n"
        f"نام خانوادگی: {last_name or '-'}\n"
        f"شماره موبایل: {phone_number or '-'}\n"
        f"ایمیل: {email or '-'}\n"
        f"جنسیت: {gender or '-'}\n"
        f"شهر: {city or '-'}\n"
        f"تاریخ تولد: {year_birthdate}/{month_birthdate}/{day_birthdate}\n\n"
        "لطفا نوع حساب خود را انتخاب کنید:",
        reply_markup=get_main_menu_keyboard(**menu_flags , state = "starter"),
    )

    

@router.message(F.text == "بازگشت به منو اصلی")
async def choose_jobseeker_handler(message: Message, state: FSMContext):
    status_response = await get_user_status(message)
    menu_flags = extract_menu_flags(status_response)
    await message.answer(
            "منو اصلی:\n"
            "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=get_main_menu_keyboard(**menu_flags , state = "starter")
        )
    return