from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.infrastructure.backend.bot_user_api import create_company_profile, create_jobseeker_profile

import traceback

from app.features.auth.permissions import (
    is_admin_user,
    is_registered_user,
    extract_menu_flags,
)
from app.features.auth.states import RegisterStates
from app.infrastructure.backend.bot_user_api import (
    get_user_status,
    register_or_update_user,
)
from app.infrastructure.backend.client import BackendAPIError
from app.shared.keyboards.contact import get_contact_keyboard
from app.shared.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
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
        "لطفاً نام و نام خانوادگی خود را وارد کنید."
    )
    await state.set_state(RegisterStates.waiting_for_full_name)


@router.message(RegisterStates.waiting_for_full_name, F.text)
async def get_full_name_handler(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name) < 3:
        await message.answer("لطفاً نام و نام خانوادگی خود را کامل وارد کنید.")
        return

    await state.update_data(full_name=full_name)

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
    data = await state.get_data()

    full_name = data.get("full_name")
    phone_number = data.get("phone_number")
    user_id = message.from_user.id if message.from_user else None

    try:
        backend_response = await register_or_update_user(
            message=message,
            registered_full_name=full_name,
            phone_number=phone_number,
            user_id=user_id,
        )

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

    is_admin = is_admin_user(backend_response)
    menu_flags = extract_menu_flags(backend_response)
    menu_flags["is_bot_bale_member"] = True
    await state.set_state(RegisterStates.choose_type_of_customer)
    user = message.from_user

    await message.answer(
        "ثبت‌نام شما با موفقیت انجام شد ✅\n\n"
        f"شناسه کاربر بله: {user.id if user else '-'}\n"
        f"شناسه چت: {message.chat.id if message.chat else '-'}\n"
        f"نام بله: {user.first_name if user and user.first_name else '-'}\n"
        f"نام خانوادگی بله: {user.last_name if user and user.last_name else '-'}\n"
        f"نام کاربری: {user.username if user and user.username else '-'}\n"
        f"نام و نام خانوادگی ثبت‌شده: {full_name or '-'}\n"
        f"شماره موبایل: {phone_number or '-'}\n"
        f"نقش کاربر: {'مدیر' if is_admin else 'مشتری'}\n\n"
        "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=get_main_menu_keyboard(**menu_flags),
    )

    


@router.message(RegisterStates.waiting_for_phone_number)
async def invalid_phone_input_handler(message: Message):
    await message.answer(
        "لطفاً شماره موبایل را فقط از طریق دکمه «ارسال شماره موبایل» ارسال کنید.",
        reply_markup=get_contact_keyboard(),
    )



@router.message(F.text == "کارجو")
async def choose_jobseeker_handler(message: Message, state: FSMContext):

    try:
        status_response = await get_user_status(message)
    except Exception as e:
        print("Get user status error:", e)
        await message.answer(
            "خطا در دریافت اطلاعات کاربر. لطفاً دوباره تلاش کنید."
        )
        return

    menu_flags = extract_menu_flags(status_response)

    # ✅ اگر قبلاً پروفایل کارجویی دارد
    if menu_flags["is_jobseeker_member"]:

        await message.answer(
            "شما قبلاً پروفایل کارجویی ساخته‌اید ✅",
            reply_markup=get_main_menu_keyboard(**menu_flags,state = "jobseeker")
        )

        await state.clear()
        return

    # ✅ اگر ندارد → بساز
    try:
        await create_jobseeker_profile(message)

    except Exception as e:
        print("Create jobseeker profile error:", e)
        await message.answer(
            "فعلاً امکان ساخت پروفایل کارجو وجود ندارد. لطفاً دوباره تلاش کنید."
        )
        return

    # ✅ بعد از ساخت → دوباره وضعیت بگیر (خیلی مهم برای sync بودن)
    try:
        status_response = await get_user_status(message)
        menu_flags = extract_menu_flags(status_response)
    except Exception as e:
        print("Refresh user status error:", e)
        return

    await message.answer(
        "پروفایل کارجویی شما با موفقیت ساخته شد ✅",
        reply_markup=get_main_menu_keyboard(**menu_flags, state = "jobseeker")
    )

    await state.clear()






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