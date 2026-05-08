from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from app.infrastructure.backend.bot_user_api import create_company_profile
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from app.features.auth.permissions import extract_menu_flags
from app.features.company.profile.api import get_company_profile_status
from app.features.company.profile.states import CompanyProfileCreateStates

from .formatter import get_choice_label
from .keyboards import (
    get_attendance_type_inline_keyboard,
    get_cooperation_type_inline_keyboard,
    get_degree_inline_keyboard,
    get_job_title_inline_keyboard,
    get_minimum_work_experiencee_inline_keyboard,
    get_working_days_inline_keyboard,
    get_overtime_inline_keyboard,
    get_working_hours_inline_keyboard,
    get_salary_type_inline_keyboard,
)
from .states import CompanyJobPostCreateStates
from .api import create_company_jobpost

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "ثبت نیازمندی جدید")
async def choose_company_handler(message: Message, state: FSMContext):
    profile_status = None

    try:
        profile_status = await get_company_profile_status(message.chat.id)
    except Exception as e:
        logger.exception("Get company profile status error: %s", e)
        profile_status = None

    if profile_status:
        if profile_status.get("is_registration_complete") is True:
            await message.answer(
                "برای ثبت نیازمندی جدید، لطفاً عنوان شغلی را انتخاب کنید.",
                reply_markup=await get_job_title_inline_keyboard()
            )
            await state.set_state(CompanyJobPostCreateStates.waiting_for_job_title)
            return

        await message.answer(
            "برای ثبت نیازمندی جدید، ابتدا باید پروفایل کارفرمایی خود را تکمیل کنید.\n\n"
            "لطفاً نام سازمان خود را وارد کنید."
        )
        await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)
        return

    try:
        await create_company_profile(message)
    except Exception as e:
        logger.exception("Create company profile error: %s", e)
        await message.answer(
            "فعلاً امکان ساخت پروفایل کارفرما وجود ندارد. لطفاً دوباره تلاش کنید."
        )
        return

    await message.answer(
        "پروفایل کارفرمایی شما ایجاد شد ✅\n"
        "برای ثبت نیازمندی جدید، ابتدا باید پروفایل خود را تکمیل کنید.\n\n"
        "لطفاً نام سازمان خود را وارد کنید."
    )
    await state.set_state(CompanyProfileCreateStates.waiting_for_company_name)


# -------------------------
# Job Title
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_job_title,
    F.data.startswith("job_title:")
)
async def job_title_handler(callback: CallbackQuery, state: FSMContext):
    job_title = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(job_title=job_title)

    await callback.message.edit_text(
        "لطفاً نوع همکاری را انتخاب کنید:",
        reply_markup=await get_cooperation_type_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_cooperation_type)
    await callback.answer()


# -------------------------
# Cooperation Type
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_cooperation_type,
    F.data.startswith("cooperation_type:")
)
async def cooperation_type_handler(callback: CallbackQuery, state: FSMContext):
    cooperation_type = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(cooperation_type=cooperation_type)

    await callback.message.edit_text(
        "لطفاً مدرک مورد نظر را انتخاب کنید:",
        reply_markup=await get_degree_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_degree)
    await callback.answer()


# -------------------------
# Degree
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_degree,
    F.data.startswith("jobpost_degree:")
)
async def degree_handler(callback: CallbackQuery, state: FSMContext):
    degree = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(degree=degree)

    await callback.message.edit_text(
        "لطفاً حداقل سابقه کاری مورد نظر را انتخاب کنید:",
        reply_markup=await get_minimum_work_experiencee_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_minimum_work_experience)
    await callback.answer()


# -------------------------
# Minimum Work Experience
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_minimum_work_experience,
    F.data.startswith("minimum_work_experience:")
)
async def minimum_work_experience_handler(callback: CallbackQuery, state: FSMContext):
    minimum_work_experience = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(minimum_work_experience=minimum_work_experience)

    await callback.message.edit_text(
        "مهارت‌های الزامی را وارد کنید.\n"
        "مثال: Python، SQL، Power BI"
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_required_skills)
    await callback.answer()


# -------------------------
# Required Skills
# -------------------------
@router.message(CompanyJobPostCreateStates.waiting_for_required_skills, F.text)
async def required_skills_handler(message: Message, state: FSMContext):
    required_skills = message.text.strip()
    await state.update_data(required_skills=required_skills)

    await message.answer(
        "شرح وظایف شغلی را وارد کنید.\n"
        "لطفاً به‌صورت مختصر بنویسید."
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_job_description)


# -------------------------
# Job Description
# -------------------------
@router.message(CompanyJobPostCreateStates.waiting_for_job_description, F.text)
async def job_description_handler(message: Message, state: FSMContext):
    job_description = message.text.strip()
    await state.update_data(job_description=job_description)

    await message.answer(
        "لطفاً نحوه حضور را انتخاب کنید:",
        reply_markup=await get_attendance_type_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_attendance_type)


# -------------------------
# Attendance Type
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_attendance_type,
    F.data.startswith("attendance_type:")
)
async def attendance_type_handler(callback: CallbackQuery, state: FSMContext):
    attendance_type = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(attendance_type=attendance_type)

    await callback.message.edit_text(
        "لطفاً روزهای کاری مورد نظر را انتخاب کنید:",
        reply_markup=await get_working_days_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_working_days)
    await callback.answer()


# -------------------------
# Working Days
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_working_days,
    F.data.startswith("working_days:")
)
async def working_days_handler(callback: CallbackQuery, state: FSMContext):
    working_days = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(working_days=working_days)

    await callback.message.edit_text(
        "آیا اضافه‌کاری دارد؟",
        reply_markup=await get_overtime_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_has_overtime)
    await callback.answer()


# -------------------------
# Has Overtime
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_has_overtime,
    F.data.startswith("has_over_time:")
)
async def has_overtime_handler(callback: CallbackQuery, state: FSMContext):
    raw_value = callback.data.split(":", maxsplit=1)[-1]
    has_overtime = raw_value == "True"

    await state.update_data(has_overtime=has_overtime)

    await callback.message.edit_text(
        "ساعات کاری را انتخاب کنید:",
        reply_markup=await get_working_hours_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_working_hours)
    await callback.answer()


# -------------------------
# Working Hours
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_working_hours,
    F.data.startswith("working_hours:")
)
async def working_hours_handler(callback: CallbackQuery, state: FSMContext):
    working_hours = callback.data.split(":", maxsplit=1)[-1]

    if working_hours == "other":
        await state.update_data(working_hours=working_hours)
        await callback.message.edit_text(
            "لطفاً ساعات کاری مدنظر را به‌صورت دقیق توضیح دهید."
        )
        await state.set_state(CompanyJobPostCreateStates.waiting_for_working_hours_description)
        await callback.answer()
        return

    await state.update_data(
        working_hours=working_hours,
        working_hours_description=""
    )

    await callback.message.edit_text(
        "نوع حقوق را انتخاب کنید:",
        reply_markup=await get_salary_type_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_is_salary_negotiable)
    await callback.answer()


@router.message(
    CompanyJobPostCreateStates.waiting_for_working_hours_description,
    F.text
)
async def working_hours_description_handler(message: Message, state: FSMContext):
    working_hours_description = message.text.strip()

    await state.update_data(
        working_hours_description=working_hours_description
    )

    await message.answer(
        "نوع حقوق را انتخاب کنید:",
        reply_markup=await get_salary_type_inline_keyboard()
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_is_salary_negotiable)


# -------------------------
# Salary Type
# -------------------------
@router.callback_query(
    CompanyJobPostCreateStates.waiting_for_is_salary_negotiable,
    F.data.startswith("salary:")
)
async def salary_type_handler(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", maxsplit=1)[1]

    if value == "negotiable":
        await state.update_data(
            is_salary_negotiable=True,
            salary_description="توافقی"
        )

        await callback.message.edit_text("✅ حقوق به‌صورت توافقی ثبت شد.")
        await callback.message.answer(
            "مزایا و تسهیلات شغلی را وارد کنید.\n"
            "اگر مزایایی ندارد، بنویسید: ندارد"
        )
        await state.set_state(CompanyJobPostCreateStates.waiting_for_is_benefits)
        await callback.answer()
        return

    if value == "fixed":
        await callback.message.edit_text(
            "لطفاً حقوق یا توضیحات حقوق را وارد کنید.\n"
            "مثال:\n"
            "۲۵ میلیون تومان\n"
            "یا\n"
            "از ۲۰ تا ۳۰ میلیون"
        )
        await state.set_state(CompanyJobPostCreateStates.waiting_for_is_salary_description)
        await callback.answer()
        return

    await callback.answer("گزینه نامعتبر است.", show_alert=True)


@router.message(
    CompanyJobPostCreateStates.waiting_for_is_salary_description,
    F.text
)
async def salary_description_handler(message: Message, state: FSMContext):
    salary_description = message.text.strip()

    await state.update_data(
        is_salary_negotiable=False,
        salary_description=salary_description
    )

    await message.answer("✅ اطلاعات حقوق ثبت شد.")
    await message.answer(
        "مزایا و تسهیلات شغلی را وارد کنید.\n"
        "اگر مزایایی ندارد، بنویسید: ندارد"
    )
    await state.set_state(CompanyJobPostCreateStates.waiting_for_is_benefits)


# -------------------------
# Benefits + Save To DB
# -------------------------
@router.message(CompanyJobPostCreateStates.waiting_for_is_benefits, F.text)
async def benefits_handler(message: Message, state: FSMContext):
    benefits = message.text.strip()
    await state.update_data(benefits=benefits)

    data = await state.get_data()

    payload = {
        "chat_id": message.from_user.id,
        "job_title": data.get("job_title"),
        "cooperation_type": data.get("cooperation_type"),
        "degree": data.get("degree"),
        "minimum_work_experience": data.get("minimum_work_experience"),
        "required_skills": data.get("required_skills"),
        "job_description": data.get("job_description"),
        "attendance_type": data.get("attendance_type"),
        "working_days": data.get("working_days"),
        "has_overtime": data.get("has_overtime", False),
        "working_hours": data.get("working_hours"),
        "working_hours_description": data.get("working_hours_description"),
        "is_salary_negotiable": data.get("is_salary_negotiable", False),
        "salary_description": data.get("salary_description"),
        "benefits": data.get("benefits"),
    }

    try:
        await create_company_jobpost(payload)
    except Exception as e:
        logger.exception("Create company job post error: %s", e)
        await message.answer(
            "در ثبت آگهی شغلی خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return

    job_title_label = await get_choice_label("job_title", data.get("job_title"))
    cooperation_type_label = await get_choice_label("cooperation_type", data.get("cooperation_type"))
    degree_label = await get_choice_label("degree", data.get("degree"))
    min_exp_label = await get_choice_label("minimum_work_experience", data.get("minimum_work_experience"))
    attendance_type_label = await get_choice_label("attendance_type", data.get("attendance_type"))
    working_days_label = await get_choice_label("working_days", data.get("working_days"))
    working_hours_label = await get_choice_label("working_hours", data.get("working_hours"))

    if data.get("working_hours") == "other" and data.get("working_hours_description"):
        final_working_hours = data.get("working_hours_description")
    else:
        final_working_hours = working_hours_label or data.get("working_hours")

    overtime_text = "دارد" if data.get("has_overtime") else "ندارد"
    salary_text = (
        "توافقی"
        if data.get("is_salary_negotiable")
        else (data.get("salary_description") or "-")
    )

    summary_text = (
        "✅ نیازمندی شما با موفقیت ثبت شد.\n\n"
        "خلاصه اطلاعات:\n\n"
        f"عنوان شغلی: {job_title_label or data.get('job_title')}\n"
        f"نوع همکاری: {cooperation_type_label or data.get('cooperation_type')}\n"
        f"مدرک: {degree_label or data.get('degree')}\n"
        f"حداقل سابقه کار: {min_exp_label or data.get('minimum_work_experience')}\n"
        f"مهارت‌های الزامی: {data.get('required_skills')}\n"
        f"شرح شغل: {data.get('job_description')}\n"
        f"نحوه حضور: {attendance_type_label or data.get('attendance_type')}\n"
        f"روزهای کاری: {working_days_label or data.get('working_days')}\n"
        f"اضافه‌کاری: {overtime_text}\n"
        f"ساعات کاری: {final_working_hours}\n"
        f"حقوق: {salary_text}\n"
        f"مزایا: {data.get('benefits')}\n"
    )

    await message.answer(summary_text)

    try:
        profile_status = await get_company_profile_status(chat_id=message.from_user.id)

        if profile_status:
            menu_flags = extract_menu_flags(profile_status)
            menu_flags["is_bot_bale_member"] = True
            menu_flags["is_company_member"] = True

            await message.answer(
                "از منوی اصلی می‌توانید عملیات بعدی را انجام دهید.",
                reply_markup=get_main_menu_keyboard(**menu_flags),
            )
    except Exception as e:
        logger.exception("Error loading profile for main menu: %s", e)

    await state.clear()
