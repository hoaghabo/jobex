from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .states import ResumeJobSeekerUploadStates

router = Router()


@router.message(F.text == "آپلود فایل رزومه")
async def ask_for_resume_file_handler(message: Message, state: FSMContext):
    await message.answer(
        "لطفاً فایل رزومه خود را با فرمت PDF ارسال کنید."
    )

    await state.set_state(
        ResumeJobSeekerUploadStates.waiting_for_resume_upload
    )



@router.message(
    ResumeJobSeekerUploadStates.waiting_for_resume_upload,
    F.document
)
async def receive_resume_file_handler(message: Message, state: FSMContext):
    document = message.document

    max_size = 5 * 1024 * 1024  # 5MB

    if document.file_size and document.file_size > max_size:
        await message.answer(
            "حجم فایل رزومه نباید بیشتر از ۵ مگابایت باشد."
        )
        return

    file_name = document.file_name or ""

    is_pdf_by_mime = document.mime_type == "application/pdf"
    is_pdf_by_name = file_name.lower().endswith(".pdf")

    if not (is_pdf_by_mime or is_pdf_by_name):
        await message.answer(
            "فرمت فایل معتبر نیست. لطفاً فقط فایل PDF ارسال کنید."
        )
        return

    await state.update_data(
        resume_file_id=document.file_id,
        resume_file_unique_id=document.file_unique_id,
        resume_file_name=document.file_name,
        resume_mime_type=document.mime_type,
        resume_file_size=document.file_size,
    )

    await message.answer(
        "فایل رزومه شما با موفقیت دریافت شد ✅"
    )

    # اگر بعد از آپلود رزومه می‌خوای مرحله بعدی رو شروع کنی:
    # await state.set_state(ResumeJobSeekerCreateStates.waiting_for_degree)
    # await message.answer("لطفاً مدرک تحصیلی خود را انتخاب کنید:", reply_markup=await get_degree_inline_keyboard())

    # اگر همین‌جا کار تمام است:
    # await state.clear()
