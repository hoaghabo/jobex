from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def jobseeker_products_keyboard(products: list) -> InlineKeyboardMarkup:
    buttons = []

    for product in products:
        product_id = product.get("id")
        title = product.get("title", "محصول بدون نام")

        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"pay_product:{product_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


