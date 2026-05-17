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
from app.infrastructure.backend.client import BackendAPIError
from .api import get_my_company_list , format_companies_list , get_my_company_id , format_single_company_info , edit_my_company_info
from app.features.company.main_menu.keyboards import get_company_main_menu
from .keyboards import get_my_company_list_inline_keyboard , get_company_edit_keyboard , build_back_button
from .state import EditMyCompanyProfileStates
from app.features.company.create_company_profile.keyboards import get_membership_role_inline_keyboard , get_city_inline_keyboard , get_organization_size_inline_keyboard
from app.features.company.create_company_profile.handlers import start_create_company_handler
router = Router()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


@router.message(F.text == "شرکت های من")
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
    is_registered = menu_flags.get("is_bot_bale_member", False)

    if not is_registered:
        await message.answer(
            "ابتدا باید ثبت‌نام کنید.\n"
            "لطفاً نام و نام خانوادگی خود را وارد کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegisterStates.waiting_for_full_name)
        return

    await message.answer(
        "---------------------------لیست شرکت های من-----------------------",
        reply_markup=ReplyKeyboardRemove()
    )

    empty_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="ثبت شرکت",
                    callback_data="create_company_From_my_company_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="بازگشت",
                    callback_data="back_my_company_list_menu"
                )
            ]
        ]
    )

    try:
        data = await get_my_company_list(message.chat.id)
    except Exception as e:
        print("Get my company list error:", e)

        error_text = str(e)

        if "status=404" in error_text or "کاربر عضو هیچ شرکتی نیست" in error_text:
            await message.answer(
                "شما هنوز هیچ شرکتی ثبت نکرده‌اید.\n\n"
                "ابتدا باید یک شرکت ثبت کنید.",
                reply_markup=empty_keyboard
            )
            await state.clear()
            return

        await message.answer(
            "خطا در دریافت لیست شرکت‌ها. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="بازگشت",
                            callback_data="back_my_company_list_menu"
                        )
                    ]
                ]
            )
        )
        return

    if not data:
        data = {}

    companies = data.get("results", [])
    if not isinstance(companies, list):
        companies = []

    if len(companies) == 0:
        await message.answer(
            "شما هنوز هیچ شرکتی ثبت نکرده‌اید.\n\n"
            "ابتدا باید یک شرکت ثبت کنید.",
            reply_markup=empty_keyboard
        )
        await state.clear()
        return

    try:
        keyboard, company_count = await get_my_company_list_inline_keyboard(
            message.chat.id
        )
    except Exception as e:
        print("Build company keyboard error:", e)
        await message.answer(
            "خطا در ساخت لیست شرکت‌ها. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="بازگشت",
                            callback_data="back_my_company_list_menu"
                        )
                    ]
                ]
            )
        )
        return

    try:
        text = format_companies_list(data)
    except Exception as e:
        print("Format company list error:", e)
        text = "لیست شرکت‌های شما:"

    await message.answer(
        text,
        reply_markup=keyboard
    )
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_company)

@router.callback_query(F.data.startswith("create_company_From_my_company_list"))
async def create_company_from_company_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await callback.message.delete()
    except Exception as e:
        print("Delete message error:", e)

    await start_create_company_handler(callback.message, state)



    

@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_choose_company,
    (F.data.startswith("company_list:")) | (F.data.startswith("back_to_company_info:"))
)
async def my_company_info(callback: CallbackQuery , state : FSMContext):

    company_id = callback.data.split(":")[-1]

    data = await get_my_company_id(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=data)

    await callback.message.edit_text(
        text,
        reply_markup=await get_company_edit_keyboard(company_id)
    )
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)




@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_choose_Edit_action,
    F.data.startswith("back_my_company_list")
)
async def my_company_info(callback: CallbackQuery , state : FSMContext):
    data = await get_my_company_list(
        chat_id=callback.message.chat.id
    )

    text = format_companies_list(data=data)

    keyboard, _ = await get_my_company_list_inline_keyboard(
        callback.message.chat.id
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_company)




@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_choose_company,
    F.data.startswith("back_my_company_list")
)
async def my_company_info(callback: CallbackQuery , state : FSMContext):
    await callback.answer()

    await callback.message.delete()

    await callback.message.answer(
        "کارفرمای عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup= await get_company_main_menu()
    )

    await state.clear()
    

@router.callback_query(
    F.data.startswith("edit_company:name:")
)
async def start_edit_company_name(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()

    # حذف پیام info قبلی
    await callback.message.delete()

    # ارسال پیام درخواست نام جدید
    sent_message = await callback.message.answer(
        "لطفاً برای شروع، نام سازمان خود را وارد کنید.",
        reply_markup=build_back_button(f"back_to_company_info:{company_id}")
    )

    # ذخیره همه چیز در state
    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(EditMyCompanyProfileStates.waiting_for_edit_company_name)



@router.message(
    EditMyCompanyProfileStates.waiting_for_edit_company_name,
    F.text
)
async def edit_company_name_handler(message: Message, state: FSMContext):
    # 1) گرفتن و تمیز کردن ورودی
    company_name = message.text.strip()

    # می‌تونی اینجا validation هم بذاری (مثلاً طول، کاراکتر مجاز، ...)
    if not company_name:
        await message.answer("❌ نام شرکت نمی‌تواند خالی باشد. لطفاً دوباره وارد کن.")
        return

    # 2) گرفتن داده‌های ذخیره‌شده در state (مثل company_id و شاید message_id اصلی)
    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")  # اگر ذخیره کرده باشی

    if company_id is None:
        await message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "company_name": company_name
    }

    # 3) صدا زدن API برای ویرایش شرکت
    try:
        await edit_my_company_info(
            chat_id=message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        # اگر همچین خطایی داری، پیام بک‌اند رو به کاربر نشان بده
        error_text = getattr(e, "body", None) or str(e)
        await message.answer(f"❌ خطا در ویرایش نام شرکت:\n{error_text}")
        return

    # 4) پاک کردن پیام ورودی کاربر (اختیاری ولی تمیزتره)
    try:
        await message.delete()
    except Exception:
        # اگر نتونست حذف کنه، اشکالی نداره، نادیده می‌گیریم
        pass
    # 5) گرفتن اطلاعات جدید شرکت بعد از ویرایش
    company_data = await get_my_company_id(
        chat_id=message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)

    # ✅ 6) اول پیام موفقیت
    success_text = "✅ نام شرکت با موفقیت ویرایش شد.\n\n" + text

    # ✅ 7) سپس صفحه info را edit کن
    if info_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=info_message_id,
                text=success_text,
                reply_markup=edit_keyboard
            )
        except Exception:
            # اگر پیام پیدا نشد، fallback به ارسال پیام جدید
            await message.answer(
                text,
                reply_markup=edit_keyboard
            )
    else:
        await message.answer(
            text,
            reply_markup=edit_keyboard
        )

    # ✅ 8) پاک کردن state
    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)



@router.callback_query(
    F.data.startswith("edit_company:role:")
)
async def start_edit_company_role(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()
    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً نقش خود در سازمان را انتخاب کنید.",
        reply_markup=await get_membership_role_inline_keyboard()
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(
        EditMyCompanyProfileStates.waiting_for_edit_company_role
    )

@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_edit_company_role,
    F.data.startswith("membership_role:") & (F.data != "membership_role:back")
)
async def edit_company_role_handler(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[-1]
    

    await callback.answer()

    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await callback.message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "role": role
    }

    try:
        await edit_my_company_info(
            chat_id=callback.message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await callback.message.answer(f"❌ خطا در ویرایش نقش:\n{error_text}")
        return

    company_data = await get_my_company_id(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)
    success_text = "✅ نقش با موفقیت ویرایش شد.\n\n" + text

    try:
        await callback.message.edit_text(
            text=success_text,
            reply_markup=edit_keyboard
        )
    except Exception:
        await callback.message.answer(
            text=success_text,
            reply_markup=edit_keyboard
        )

    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)

@router.callback_query(
    F.data.startswith("edit_company:size:")
)
async def start_edit_organization_size(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()
    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً اندازه سازمان را انتخاب کنید.",
        reply_markup=await get_organization_size_inline_keyboard()
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(
        EditMyCompanyProfileStates.waiting_for_edit_organization_size
    )

@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_edit_organization_size,
    F.data.startswith("organization_size:") & (F.data != "organization_size:back")
)
async def edit_company_size_handler(callback: CallbackQuery, state: FSMContext):
    organization_size = callback.data.split(":")[-1]
    if organization_size == "back":
        return  # اجازه بده هندلر back اجرا شود

    await callback.answer()

    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await callback.message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "organization_size": organization_size
    }

    try:
        await edit_my_company_info(
            chat_id=callback.message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await callback.message.answer(f"❌ خطا در ویرایش اندازه سازمان:\n{error_text}")
        return

    company_data = await get_my_company_id(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)
    success_text = "✅ اندازه سازمان با موفقیت ویرایش شد.\n\n" + text

    try:
        await callback.message.edit_text(
            text=success_text,
            reply_markup=edit_keyboard
        )
    except Exception:
        await callback.message.answer(
            text=success_text,
            reply_markup=edit_keyboard
        )

    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)


@router.callback_query(
    F.data.startswith("edit_company:city:")
)
async def start_edit_company_city(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()
    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً شهر سازمان را انتخاب کنید.",
        reply_markup=await get_city_inline_keyboard()
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(
        EditMyCompanyProfileStates.waiting_for_edit_city
    )


@router.callback_query(
    EditMyCompanyProfileStates.waiting_for_edit_city,
    F.data.startswith("city:") & (F.data != "city:back")
)
async def edit_company_city_handler(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split(":")[-1]

    await callback.answer()

    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await callback.message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "city": city
    }

    try:
        await edit_my_company_info(
            chat_id=callback.message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await callback.message.answer(f"❌ خطا در ویرایش شهر:\n{error_text}")
        return

    company_data = await get_my_company_id(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)
    success_text = "✅ شهر با موفقیت ویرایش شد.\n\n" + text

    try:
        await callback.message.edit_text(
            text=success_text,
            reply_markup=edit_keyboard
        )
    except Exception:
        await callback.message.answer(
            text=success_text,
            reply_markup=edit_keyboard
        )

    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)


@router.callback_query(
    F.data.startswith("edit_company:address:")
)
async def start_edit_company_address(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()

    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً آدرس کامل سازمان را وارد کنید.",
        reply_markup=build_back_button(f"back_to_company_info:{company_id}")
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(EditMyCompanyProfileStates.waiting_for_edit_full_address)


@router.message(
    EditMyCompanyProfileStates.waiting_for_edit_full_address,
    F.text
)
async def edit_company_address_handler(message: Message, state: FSMContext):
    # 1) گرفتن و تمیز کردن ورودی
    full_address = message.text.strip()

    # validation
    if not full_address:
        await message.answer("❌ آدرس شرکت نمی‌تواند خالی باشد. لطفاً دوباره وارد کن.")
        return

    # 2) گرفتن داده‌های ذخیره‌شده در state
    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "full_address": full_address
    }

    # 3) صدا زدن API برای ویرایش شرکت
    try:
        await edit_my_company_info(
            chat_id=message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await message.answer(f"❌ خطا در ویرایش آدرس شرکت:\n{error_text}")
        return

    # 4) پاک کردن پیام ورودی کاربر
    try:
        await message.delete()
    except Exception:
        pass

    # 5) گرفتن اطلاعات جدید شرکت بعد از ویرایش
    company_data = await get_my_company_id(
        chat_id=message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)

    success_text = "✅ آدرس شرکت با موفقیت ویرایش شد.\n\n" + text

    # 6) ویرایش پیام info
    if info_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=info_message_id,
                text=success_text,
                reply_markup=edit_keyboard
            )
        except Exception:
            await message.answer(
                text,
                reply_markup=edit_keyboard
            )
    else:
        await message.answer(
            text,
            reply_markup=edit_keyboard
        )

    # 7) پاک کردن state
    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)



@router.callback_query(
    F.data.startswith("edit_company:industry:")
)
async def start_edit_company_industry(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()

    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً صنعت سازمان را وارد کنید.",
        reply_markup=build_back_button(f"back_to_company_info:{company_id}")
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(EditMyCompanyProfileStates.waiting_for_edit_industry)



@router.message(
    EditMyCompanyProfileStates.waiting_for_edit_industry,
    F.text
)
async def edit_company_industry_handler(message: Message, state: FSMContext):
    # 1) گرفتن و تمیز کردن ورودی
    industry = message.text.strip()

    # validation
    if not industry:
        await message.answer("❌ صنعت شرکت نمی‌تواند خالی باشد. لطفاً دوباره وارد کن.")
        return

    # 2) گرفتن داده‌های ذخیره‌شده در state
    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "industry": industry
    }

    # 3) صدا زدن API برای ویرایش شرکت
    try:
        await edit_my_company_info(
            chat_id=message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await message.answer(f"❌ خطا در ویرایش صنعت شرکت:\n{error_text}")
        return

    # 4) پاک کردن پیام ورودی کاربر
    try:
        await message.delete()
    except Exception:
        pass

    # 5) گرفتن اطلاعات جدید شرکت بعد از ویرایش
    company_data = await get_my_company_id(
        chat_id=message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)

    success_text = "✅ صنعت شرکت با موفقیت ویرایش شد.\n\n" + text

    # 6) ویرایش پیام info
    if info_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=info_message_id,
                text=success_text,
                reply_markup=edit_keyboard
            )
        except Exception:
            await message.answer(
                text,
                reply_markup=edit_keyboard
            )
    else:
        await message.answer(
            text,
            reply_markup=edit_keyboard
        )

    # 7) پاک کردن state
    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)

@router.callback_query(
    F.data.startswith("edit_company:phone:")
)
async def start_edit_company_phone(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()

    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً شماره تلفن ثابت سازمان را وارد کنید.",
        reply_markup=build_back_button(f"back_to_company_info:{company_id}")
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(EditMyCompanyProfileStates.waiting_for_edit_landline_phone)


@router.message(
    EditMyCompanyProfileStates.waiting_for_edit_landline_phone,
    F.text
)
async def edit_company_phone_handler(message: Message, state: FSMContext):
    # 1) گرفتن و تمیز کردن ورودی
    landline_phone = message.text.strip()

    # validation
    if not landline_phone:
        await message.answer("❌ شماره تلفن شرکت نمی‌تواند خالی باشد. لطفاً دوباره وارد کن.")
        return

    # 2) گرفتن داده‌های ذخیره‌شده در state
    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "landline_phone": landline_phone
    }

    # 3) صدا زدن API برای ویرایش شرکت
    try:
        await edit_my_company_info(
            chat_id=message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await message.answer(f"❌ خطا در ویرایش شماره تلفن شرکت:\n{error_text}")
        return

    # 4) پاک کردن پیام ورودی کاربر
    try:
        await message.delete()
    except Exception:
        pass

    # 5) گرفتن اطلاعات جدید شرکت بعد از ویرایش
    company_data = await get_my_company_id(
        chat_id=message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)

    success_text = "✅ شماره تلفن شرکت با موفقیت ویرایش شد.\n\n" + text

    # 6) ویرایش پیام info
    if info_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=info_message_id,
                text=success_text,
                reply_markup=edit_keyboard
            )
        except Exception:
            await message.answer(
                text,
                reply_markup=edit_keyboard
            )
    else:
        await message.answer(
            text,
            reply_markup=edit_keyboard
        )

    # 7) پاک کردن state
    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)

@router.callback_query(
    F.data.startswith("edit_company:website:")
)
async def start_edit_company_website(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]

    await callback.answer()

    await callback.message.delete()

    sent_message = await callback.message.answer(
        "لطفاً آدرس وبسایت سازمان را وارد کنید.",
        reply_markup=build_back_button(f"back_to_company_info:{company_id}")
    )

    await state.update_data(
        edit_company_id=company_id,
        edit_prompt_message_id=sent_message.message_id
    )

    await state.set_state(EditMyCompanyProfileStates.waiting_for_edit_website)


@router.message(
    EditMyCompanyProfileStates.waiting_for_edit_website,
    F.text
)
async def edit_company_website_handler(message: Message, state: FSMContext):
    website = message.text.strip()

    if not website:
        await message.answer("❌ وبسایت شرکت نمی‌تواند خالی باشد. لطفاً دوباره وارد کن.")
        return

    # اگر scheme نداشت، https اضافه کن
    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"

    data = await state.get_data()
    company_id = data.get("edit_company_id")
    info_message_id = data.get("edit_prompt_message_id")

    if company_id is None:
        await message.answer("❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو.")
        await state.clear()
        return

    payload = {
        "website": website
    }

    try:
        await edit_my_company_info(
            chat_id=message.chat.id,
            company_id=company_id,
            payload=payload
        )
    except BackendAPIError as e:
        error_text = getattr(e, "body", None) or str(e)
        await message.answer(f"❌ خطا در ویرایش وبسایت شرکت:\n{error_text}")
        return

    try:
        await message.delete()
    except Exception:
        pass

    company_data = await get_my_company_id(
        chat_id=message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)
    edit_keyboard = await get_company_edit_keyboard(company_id)

    success_text = "✅ وبسایت شرکت با موفقیت ویرایش شد.\n\n" + text

    if info_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=info_message_id,
                text=success_text,
                reply_markup=edit_keyboard
            )
        except Exception:
            await message.answer(
                success_text,
                reply_markup=edit_keyboard
            )
    else:
        await message.answer(
            success_text,
            reply_markup=edit_keyboard
        )

    await state.clear()




@router.callback_query(
    (F.data == "membership_role:back") |
    (F.data == "organization_size:back") |
    (F.data == "city:back")
)
async def back_to_company_info_from_edit_choices(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    company_id = data.get("edit_company_id")

    if company_id is None:
        await callback.message.answer(
            "❌ شناسه شرکت پیدا نشد. لطفاً دوباره از منوی شرکت‌ها وارد شو."
        )
        await state.clear()
        return

    company_data = await get_my_company_id(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )

    text = format_single_company_info(data=company_data)

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_company_edit_keyboard(company_id)
        )
    except Exception:
        await callback.message.answer(
            text=text,
            reply_markup=await get_company_edit_keyboard(company_id)
        )

    await state.clear()
    await state.set_state(EditMyCompanyProfileStates.waiting_for_choose_Edit_action)

