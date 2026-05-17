from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message,ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .states import ResumeJobSeekerUploadStates
from .keyboards import cancel_keyboard
from app.features.jobseeker.jobseeker_main.keyboards import get_jobseeker_main_menu
from app.features.jobseeker.update_resume.api import patch_jobseeker_profile_me
router = Router()

# ID کانال مورد نظر (همان 5198008587)
CHANNEL_ID = "5198008587"  # توجه: فرمت کانال باید با -100 شروع شود


@router.message(F.text == "آپلود فایل رزومه")
async def ask_for_resume_file_handler(message: Message, state: FSMContext):
    remove_msg = await message.answer(
        "---------------------------ارسال فایل PDF رزومه------------------------",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "لطفاً فایل رزومه خود را با فرمت PDF ارسال کنید.",
        reply_markup=cancel_keyboard
    )


    await state.set_state(
        ResumeJobSeekerUploadStates.waiting_for_resume_upload
    )


@router.message(
    ResumeJobSeekerUploadStates.waiting_for_resume_upload,
    F.document
)
async def receive_resume_file_handler(message: Message, state: FSMContext, bot: Bot):
    document = message.document

    if not document:
        await message.answer(
            "فایلی دریافت نشد. لطفاً فایل رزومه خود را به صورت PDF ارسال کنید.",
            reply_markup=cancel_keyboard
        )
        return

    max_size = 5 * 1024 * 1024  # 5MB

    # -------------------------------------------------
    # 1) بررسی حجم فایل
    # -------------------------------------------------
    if document.file_size and document.file_size > max_size:
        await message.answer(
            "حجم فایل رزومه نباید بیشتر از ۵ مگابایت باشد.",
            reply_markup=cancel_keyboard
        )
        return

    file_name = document.file_name or "resume.pdf"

    # -------------------------------------------------
    # 2) بررسی PDF بودن فایل
    # -------------------------------------------------
    is_pdf_by_mime = document.mime_type == "application/pdf"
    is_pdf_by_name = file_name.lower().endswith(".pdf")

    if not (is_pdf_by_mime or is_pdf_by_name):
        await message.answer(
            "فرمت فایل معتبر نیست. لطفاً فقط فایل PDF ارسال کنید.",
            reply_markup=cancel_keyboard
        )
        return

    # -------------------------------------------------
    # 3) ذخیره موقت اطلاعات فایل در state
    # -------------------------------------------------
    await state.update_data(
        resume_file_id=document.file_id,
        resume_file_unique_id=document.file_unique_id,
        resume_file_name=file_name,
        resume_mime_type=document.mime_type,
        resume_file_size=document.file_size,
    )

    # -------------------------------------------------
    # 4) ارسال فایل به کانال
    # -------------------------------------------------
    try:
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=document.file_id,
            caption=(
                f"📄 فایل رزومه جدید دریافت شد:\n\n"
                f"👤 ارسال‌کننده: {message.from_user.full_name} | {message.from_user.id}\n"
                f"📎 نام فایل: {file_name}\n"
            )
        )

    except Exception as e:
        print(f"خطا در ارسال فایل به کانال: {e}")
        await message.answer(
            "متأسفانه در ارسال رزومه به کانال خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=cancel_keyboard
        )
        return

    # -------------------------------------------------
    # 5) ذخیره file_id رزومه در پروفایل کارجو
    # -------------------------------------------------
    try:
        await patch_jobseeker_profile_me({
            "chat_id": message.from_user.id,
            "resume_file_id": document.file_id
        })

    except Exception as e:
        print(f"خطا در ذخیره فایل آیدی رزومه در پروفایل کارجو: {e}")
        await message.answer(
            "رزومه شما دریافت شد، اما در ذخیره اطلاعات آن در پروفایل خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=cancel_keyboard
        )
        return

    # -------------------------------------------------
    # 6) پیام موفقیت
    # -------------------------------------------------
    await message.answer(
        "فایل رزومه شما با موفقیت دریافت شد و به بانک رزومه‌ها اضافه شد ✅"
    )

    await message.answer(
        "کارجوی عزیز لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=await get_jobseeker_main_menu()
    )

    # -------------------------------------------------
    # 7) اتمام state
    # -------------------------------------------------
    await state.clear()


@router.callback_query(F.data.startswith("cancel_resume_upload"))
async def from_upload_resume_back_to_main_menu(callback: CallbackQuery , state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "کارجوی عزیز لطفا یکی از گزینه های زیر را انتخاب کنید:",
        reply_markup=await get_jobseeker_main_menu()
    )
    await callback.answer()
    await state.clear()


@router.message(ResumeJobSeekerUploadStates.waiting_for_resume_upload,F.text)
async def send_resume_pdf_file_agein(message:Message):
    await message.answer(
        "لطفا فقط فایل pdf خود را بدون هیچ توضیحاتی ارسال کنید:",
        reply_markup=cancel_keyboard
    )