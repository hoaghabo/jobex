# features/payment/keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_payment_methods_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """کیبورد انتخاب روش پرداخت"""
    keyboard = [
        [InlineKeyboardButton(
            text="💳 زرین‌پال",
            callback_data=f"payment_method:zarinpal:{order_id}"
        )],
        [InlineKeyboardButton(
            text="🏦 کارت به کارت",
            callback_data=f"payment_method:card_to_card:{order_id}"
        )],
        [InlineKeyboardButton(
            text="💼 کیف پول بله",
            callback_data=f"payment_method:bale_wallet:{order_id}"
        )],
        [InlineKeyboardButton(
            text="🔙 بازگشت",
            callback_data=f"back_to_order:{order_id}"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_actions_keyboard(payment_id: int, method: str, payment_url: str = None) -> InlineKeyboardMarkup:
    """کیبورد اقدامات پس از ایجاد پرداخت"""
    keyboard = []
    
    # اگر لینک پرداخت موجود باشه، دکمه URL اضافه کن
    if payment_url and method in ["zarinpal", "bale_wallet"]:
        keyboard.append([InlineKeyboardButton(
            text="💳 پرداخت آنلاین",
            url=payment_url
        )])
    
    # دکمه بررسی وضعیت
    keyboard.append([InlineKeyboardButton(
        text="🔄 بررسی وضعیت",
        callback_data=f"check_payment:{payment_id}"
    )])
    
    # دکمه بازگشت
    keyboard.append([InlineKeyboardButton(
        text="🏠 بازگشت به منوی اصلی",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_back_to_payment_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """کیبورد بازگشت به انتخاب روش پرداخت"""
    keyboard = [
        [InlineKeyboardButton(
            text="🔄 تلاش مجدد",
            callback_data=f"pay_order:{order_id}"
        )],
        [InlineKeyboardButton(
            text="🏠 منوی اصلی",
            callback_data="main_menu"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_payment_success_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 بسته‌های من",
                    callback_data="my_packages"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 بازگشت به خانه",
                    callback_data="back_to_home"
                )
            ]
        ]
    )
