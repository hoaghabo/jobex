from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.features.jobseeker_buy.buy_package.api import get_jobseeker_products
from app.infrastructure.backend.bot_user_api import get_user_status
from .keyboards import jobseeker_products_keyboard
from app.features.auth.states import RegisterStates
from app.shared.keyboards.contact import get_contact_keyboard

router = Router()


def format_price(product: dict) -> str:
    price = product.get("base_price") or product.get("price") or product.get("amount") or 0
    try:
        return f"{int(float(price)):,} تومان"
    except Exception:
        return str(price)


def find_product_by_id(products: list, product_id: int):
    for product in products:
        if product.get("id") == product_id:
            return product
    return None


async def check_user_bale_membership(message: Message) -> bool:
    user_status = await get_user_status(message)
    if not user_status:
        return False
    return bool(user_status.get("is_bot_bale_member"))


@router.message(F.text == "خرید اشتراک کارجو")
async def show_jobseeker_products(message: Message, state: FSMContext):
    if not await check_user_bale_membership(message):
        await message.answer(
            "برای استفاده از ربات، لطفاً شماره موبایل خود را فقط از طریق دکمه زیر ارسال کنید.",
            reply_markup=get_contact_keyboard(),
        )
        await state.set_state(RegisterStates.waiting_for_phone_number)
        return

    products = await get_jobseeker_products()
    if not products:
        await message.answer("در حال حاضر محصولی برای کارجو یافت نشد.")
        return

    await message.answer(
        "لطفاً یکی از اشتراک‌های کارجو را انتخاب کنید:",
        reply_markup=jobseeker_products_keyboard(products),
    )


@router.callback_query(F.data == "back:jobseeker_products")
async def back_to_jobseeker_products(callback: CallbackQuery, state: FSMContext):
    if not await check_user_bale_membership(callback.message):
        await callback.message.answer(
            "برای استفاده از ربات، لطفاً شماره موبایل خود را فقط از طریق دکمه زیر ارسال کنید.",
            reply_markup=get_contact_keyboard(),
        )
        await state.set_state(RegisterStates.waiting_for_phone_number)
        await callback.answer()
        return

    products = await get_jobseeker_products()
    if not products:
        await callback.message.edit_text("در حال حاضر محصولی برای کارجو یافت نشد.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "لطفاً یکی از اشتراک‌های کارجو را انتخاب کنید:",
        reply_markup=jobseeker_products_keyboard(products),
    )
    await callback.answer()
