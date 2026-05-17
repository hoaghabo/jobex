from aiogram import Router, F
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import logging

from app.infrastructure.backend.bot_user_api import create_company_profile
from app.shared.keyboards.main_menu import get_main_menu_keyboard
from app.features.auth.permissions import extract_menu_flags
from app.features.company.create_company_profile.api import get_company_profile_status
from app.features.company.create_company_profile.states import CompanyProfileCreateStates
from app.features.company.main_menu.keyboards import get_company_main_menu
from app.features.auth.states import RegisterStates
from .formatter import format_jobpost_detail_text
# from .keyboards import (
#     get_attendance_type_inline_keyboard,
#     get_cooperation_type_inline_keyboard,
#     get_degree_inline_keyboard,
#     get_job_title_inline_keyboard,
#     get_minimum_work_experiencee_inline_keyboard,
#     get_working_days_inline_keyboard,
#     get_overtime_inline_keyboard,
#     get_working_hours_inline_keyboard,
#     get_salary_type_inline_keyboard,
# )
from .states import CompanyJobPostListStates
from .api import get_company_jobpost_detail , delete_company_jobpost
from app.features.company.my_company_profile.api import get_my_company_list
from app.features.company.my_company_profile.keyboards import get_my_company_list_inline_keyboard
from .keyboards import get_my_company_Job_list_inline_keyboard , build_jobpost_detail_keyboard , build_empty_company_list_keyboard
from app.infrastructure.backend.bot_user_api import get_user_status
logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "آگهی شغلی های من")
async def choose_jobseeker_handler(message: Message, state: FSMContext):
    # -------------------------------------------------
    # 1) گرفتن وضعیت کاربر
    # -------------------------------------------------
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
    is_jobseeker_member = menu_flags.get("is_jobseeker_member", False)

    # -------------------------------------------------
    # 2) کاربر هنوز ثبت‌نام نکرده
    # -------------------------------------------------
    if not is_registered:
        await message.answer(
            "ابتدا باید ثبت‌نام کنید.\n"
            "لطفاً نام و نام خانوادگی خود را وارد کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegisterStates.waiting_for_full_name)
        return

    # -------------------------------------------------
    # 3) حذف کیبورد قبلی
    # -------------------------------------------------
    await message.answer(
        "---------------------------درخواست آگهی شغلی----------------------",
        reply_markup=ReplyKeyboardRemove()
    )

    # -------------------------------------------------
    # 4) گرفتن لیست شرکت‌های کاربر
    # -------------------------------------------------
    try:
        keyboard, company_count = await get_my_company_list_inline_keyboard(
            message.chat.id
        )
    except Exception as e:
        print("Build company keyboard error:", e)
        await message.answer(
            "خطا در دریافت لیست شرکت‌ها. لطفاً دوباره تلاش کنید."
        )
        return

    # -------------------------------------------------
    # 5) اگر هیچ شرکتی ثبت نشده بود
    # -------------------------------------------------
    if company_count == 0:
        await message.answer(
            "شما هنوز هیچ شرکتی ثبت نکرده‌اید.\n\n"
            "برای مشاهده آگهی‌های شغلی، ابتدا باید یک شرکت ثبت کنید.",
            reply_markup=build_empty_company_list_keyboard()
        )

        await state.clear()
        return

    # -------------------------------------------------
    # 6) نمایش لیست شرکت‌ها
    # -------------------------------------------------
    await message.answer(
        "لطفاً انتخاب کنید آگهی‌های شغلی کدام شرکت را می‌خواهید ببینید؟",
        reply_markup=keyboard
    )

    await state.set_state(
        CompanyJobPostListStates.waiting_for_choose_company
    )


@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_company,
    F.data.startswith("back_my_company_list"))
async def Back_to_company_main_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        "کارفرمای عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup=await get_company_main_menu()
    )





@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_company,
    F.data.startswith("company_list:")
)
async def job_title_handler(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":", maxsplit=1)[-1]
    await state.update_data(company_id=company_id)
    company_label = None

    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                company_label = button.text
                break
        if company_label:
            break
    await state.update_data(company_label=company_label)
    await callback.message.edit_text(
        "لطفاً عنوان شغلی خود را انتخاب کنید:",
        reply_markup=await get_my_company_Job_list_inline_keyboard(
        chat_id=callback.message.chat.id,
        company_id=company_id
    )
    )
    await state.set_state(CompanyJobPostListStates.waiting_for_choose_job_post)
    await callback.answer()



@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_job_post,
    F.data.startswith("back_my_company_job_post_to_company_list_menu")
)
async def Back_to_company_main_menu_handler(callback: CallbackQuery, state: FSMContext):
    keyboard, company_count = await get_my_company_list_inline_keyboard(
        callback.message.chat.id
    )

    await callback.message.edit_text(
        "لطفا انتخاب کنید آگهی شغلی چه شرکتی رو میخواهید ببیند؟",
        reply_markup=keyboard
    )

    await state.set_state(CompanyJobPostListStates.waiting_for_choose_company)








@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_job_post,
    F.data.startswith("job_post_list:"),
)
async def job_title_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    jobpost_id = int(callback.data.split(":", maxsplit=1)[-1])
    await state.update_data(jobpost_id=jobpost_id)

    job_post_label = None
    reply_markup = callback.message.reply_markup

    if reply_markup and reply_markup.inline_keyboard:
        for row in reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data == callback.data:
                    job_post_label = button.text
                    break
            if job_post_label:
                break

    await state.update_data(job_post_label=job_post_label)

    data = await state.get_data()
    company_id = int(data.get("company_id"))

    jobpost_detail = await get_company_jobpost_detail(
        chat_id=callback.message.chat.id,
        company_id=company_id,
        jobpost_id=jobpost_id,
    )

    text = format_jobpost_detail_text(jobpost_detail)

    edited_message = await callback.message.edit_text(
        text=text,
        reply_markup=build_jobpost_detail_keyboard(
            chat_id=callback.message.chat.id,
            company_id=company_id,
            jobpost_id=jobpost_id,
        ),
    )

    await state.update_data(
        jobpost_detail_message_id=edited_message.message_id,
        jobpost_detail_chat_id=edited_message.chat.id,
    )

    await state.set_state(
        CompanyJobPostListStates.waiting_for_choose_job_post_action
    )







@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_job_post_action,
    F.data.startswith("delete_jobpost:")
)
async def delete_job_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    status_message = None
    company_id = None
    chat_id = callback.message.chat.id

    try:
        print("DELETE CALLBACK DATA:", callback.data)

        parts = callback.data.split(":")

        if len(parts) != 4:
            data = await state.get_data()
            company_id = data.get("company_id")

            reply_markup = None
            if company_id is not None:
                reply_markup = await get_my_company_Job_list_inline_keyboard(
                    chat_id=chat_id,
                    company_id=int(company_id)
                )

            await callback.message.answer(
                "❌ اطلاعات حذف آگهی نامعتبر است.\n"
                "لطفاً دوباره از لیست آگهی‌ها اقدام کنید.",
                reply_markup=reply_markup
            )

            await state.set_state(
                CompanyJobPostListStates.waiting_for_choose_job_post
            )
            return

        _, callback_chat_id, company_id, jobpost_id = parts

        callback_chat_id = int(callback_chat_id)
        company_id = int(company_id)
        jobpost_id = int(jobpost_id)

        print("====================> chat_id:", callback_chat_id)
        print("====================> company_id:", company_id)
        print("====================> jobpost_id:", jobpost_id)

        status_message = await callback.message.answer(
            "🗑 در حال حذف آگهی شغلی...\n"
            "لطفاً چند لحظه صبر کنید."
        )

        try:
            await callback.message.delete()
        except Exception as e:
            print(f"delete message error: {e}")

        await delete_company_jobpost(
            chat_id=callback_chat_id,
            company_id=company_id,
            jobpost_id=jobpost_id,
        )

        reply_markup = await get_my_company_Job_list_inline_keyboard(
            chat_id=chat_id,
            company_id=company_id
        )

        await status_message.edit_text(
            text=(
                "✅ آگهی شغلی با موفقیت حذف شد.\n\n"
                "لطفاً عنوان شغلی بعدی را انتخاب کنید:"
            ),
            reply_markup=reply_markup
        )

        await state.set_state(
            CompanyJobPostListStates.waiting_for_choose_job_post
        )

    except ValueError as e:
        print(f"delete_job_post ValueError: {e}")

        reply_markup = None
        if company_id is not None:
            reply_markup = await get_my_company_Job_list_inline_keyboard(
                chat_id=chat_id,
                company_id=int(company_id)
            )

        if status_message:
            await status_message.edit_text(
                "❌ اطلاعات ارسال‌شده برای حذف آگهی معتبر نیست.\n"
                "لطفاً دوباره تلاش کنید.",
                reply_markup=reply_markup
            )
        else:
            await callback.message.answer(
                "❌ اطلاعات ارسال‌شده برای حذف آگهی معتبر نیست.\n"
                "لطفاً دوباره تلاش کنید.",
                reply_markup=reply_markup
            )

        await state.set_state(
            CompanyJobPostListStates.waiting_for_choose_job_post
        )

    except Exception as e:
        print(f"delete_job_post error: {e}")

        reply_markup = None
        if company_id is not None:
            try:
                reply_markup = await get_my_company_Job_list_inline_keyboard(
                    chat_id=chat_id,
                    company_id=int(company_id)
                )
            except Exception as keyboard_error:
                print(f"get job list keyboard error: {keyboard_error}")

        if status_message:
            await status_message.edit_text(
                "❌ خطایی هنگام حذف آگهی شغلی رخ داد.\n"
                "لطفاً چند لحظه بعد دوباره تلاش کنید.",
                reply_markup=reply_markup
            )
        else:
            await callback.message.answer(
                "❌ خطایی هنگام حذف آگهی شغلی رخ داد.\n"
                "لطفاً چند لحظه بعد دوباره تلاش کنید.",
                reply_markup=reply_markup
            )

        await state.set_state(
            CompanyJobPostListStates.waiting_for_choose_job_post
        )




@router.callback_query(
    CompanyJobPostListStates.waiting_for_choose_job_post_action,
    F.data.startswith("back_to_jobpost_list:"))
async def Back_to_company_main_menu_handler(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.split(":")[-1]
    chat_id=callback.message.chat.id,
    await callback.message.edit_text(
        "لطفا انتخاب کنید آگهی شغلی چه شرکتی رو میخواهید ببیند؟",
                reply_markup = await get_my_company_Job_list_inline_keyboard(
                    chat_id=chat_id,
                    company_id=int(company_id)
    ))
    await state.set_state(CompanyJobPostListStates.waiting_for_choose_job_post)




