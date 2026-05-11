from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
import traceback

from app.features.auth.permissions import is_admin_user, is_registered_user, extract_menu_flags
from app.features.auth.states import RegisterStates
from app.infrastructure.backend.bot_user_api import get_user_status, register_or_update_user
from app.infrastructure.backend.client import BackendAPIError
from app.shared.keyboards.contact import get_contact_keyboard
from app.shared.keyboards.main_menu import get_main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    status_response = await get_user_status(message)

    if status_response is None:
        await message.answer(
            "فعلاً امکان بررسی وضعیت شما وجود ندارد. لطفاً چند دقیقه دیگر دوباره تلاش کنید."
        )
        return

    if is_registered_user(status_response):
        menu_flags = extract_menu_flags(status_response)
        await message.answer(
            "خوش آمدید 👋\nاز منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=get_main_menu_keyboard(**menu_flags),
        )
        return

    await message.answer(
        "برای استفاده از ربات، لطفاً شماره موبایل خود را فقط از طریق دکمه زیر ارسال کنید.",
        reply_markup=get_contact_keyboard(),
    )
    await state.set_state(RegisterStates.waiting_for_phone_number)


@router.message(RegisterStates.waiting_for_phone_number, F.contact)
async def get_phone_contact_handler(message: Message, state: FSMContext):
    contact = message.contact

    if not contact or not contact.phone_number:
        await message.answer("شماره موبایل دریافت نشد. لطفاً دوباره تلاش کنید.", reply_markup=get_contact_keyboard())
        return

    if message.from_user and contact.user_id and contact.user_id != message.from_user.id:
        await message.answer("لطفاً فقط شماره موبایل متعلق به خودتان را ارسال کنید.", reply_markup=get_contact_keyboard())
        return

    user = message.from_user
    phone_number = contact.phone_number
    first_name = user.first_name.strip() if user and user.first_name else ""
    last_name = user.last_name.strip() if user and user.last_name else ""
    registered_full_name = f"{first_name} {last_name}".strip() or "کاربر بله"

    try:
        backend_response = await register_or_update_user(
            message=message,
            registered_full_name=registered_full_name,
            phone_number=phone_number,
            user_id=user.id if user else None,
        )
    except BackendAPIError as e:
        logger.error("Backend API Error: %s", e)
        await message.answer(
            "ثبت‌نام شما فعلاً انجام نشد. ارتباط با سرور برقرار نشد.\nلطفاً چند دقیقه دیگر دوباره تلاش کنید."
        )
        return
    except Exception as e:
        logger.exception("Unexpected Error: %s", e)
        await message.answer("خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.")
        return

    is_admin = is_admin_user(backend_response)
    menu_flags = extract_menu_flags(backend_response)
    menu_flags["is_bot_bale_member"] = True

    await message.answer(
        "ثبت‌نام شما با موفقیت انجام شد ✅\n\n"
        f"شناسه کاربر بله: {user.id if user else '-'}\n"
        f"شناسه چت: {message.chat.id if message.chat else '-'}\n"
        f"نام بله: {user.first_name if user and user.first_name else '-'}\n"
        f"نام خانوادگی بله: {user.last_name if user and user.last_name else '-'}\n"
        f"نام کاربری: {user.username if user and user.username else '-'}\n"
        f"شماره موبایل: {phone_number or '-'}\n"
        f"نقش کاربر: {'مدیر' if is_admin else 'مشتری'}\n\n"
        "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=get_main_menu_keyboard(**menu_flags),
    )
    await state.clear()


@router.message(RegisterStates.waiting_for_phone_number)
async def invalid_phone_input_handler(message: Message):
    await message.answer(
        "لطفاً شماره موبایل را فقط از طریق دکمه «ارسال شماره موبایل» ارسال کنید.",
        reply_markup=get_contact_keyboard(),
    )
