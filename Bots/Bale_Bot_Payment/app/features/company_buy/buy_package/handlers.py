from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.features.company_buy.buy_package.api import get_company_products, get_products
from .keyboards import company_products_keyboard

router = Router()


def format_price(product: dict) -> str:
    price = (
        product.get("base_price")
        or product.get("price")
        or product.get("amount")
        or 0
    )

    try:
        price = int(float(price))
        return f"{price:,} تومان"
    except Exception:
        return str(price)


def find_product_by_id(products: list, product_id: int):
    for product in products:
        if str(product.get("id")) == str(product_id):
            return product
    return None


@router.message(F.text == "خرید اشتراک کارفرما")
async def show_company_products(message: Message):
    products = await get_company_products()

    if not products:
        await message.answer("در حال حاضر محصولی برای کارفرما یافت نشد.")
        return

    await message.answer(
        "لطفاً یکی از اشتراک‌های کارفرما را انتخاب کنید:",
        reply_markup=company_products_keyboard(products),
    )


@router.callback_query(F.data == "back:company_products")
async def back_to_company_products(callback: CallbackQuery):
    products = await get_company_products()

    if not products:
        await callback.message.edit_text("در حال حاضر محصولی برای کارفرما یافت نشد.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "لطفاً یکی از اشتراک‌های کارفرما را انتخاب کنید:",
        reply_markup=company_products_keyboard(products),
    )
    await callback.answer()


