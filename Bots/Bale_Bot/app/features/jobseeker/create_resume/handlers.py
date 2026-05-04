from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

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
    get_work_location_priority_inline_keyboard
)

from .states import ResumeJobSeekerCreateStates

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
async def get_degree_callback_handler(callback: CallbackQuery, state: FSMContext):
    degree = callback.data.split(":")[-1]

    await state.update_data(degree=degree)

    await callback.answer()

    await callback.message.edit_text(
        "لطفا تاریخ تولد خود را وارد کنید\n"
        "فرمت مناسب ورودی: ۱۳۸۲/۲/۴"
    )

    await state.set_state(
        ResumeJobSeekerCreateStates.waiting_for_year_birthday
    )
