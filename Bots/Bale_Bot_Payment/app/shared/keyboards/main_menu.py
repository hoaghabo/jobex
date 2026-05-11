from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(
    is_jobseeker_member: bool = False,
    is_company_member: bool = False,
    is_bot_bale_member: bool = False,
) -> ReplyKeyboardMarkup:
    keyboard = []

    if not is_bot_bale_member:
        keyboard.append(
            [KeyboardButton(text="عضویت در بات")]
        )
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
        )

    if is_bot_bale_member:
        keyboard.append(
            [
                KeyboardButton(text="خرید اشتراک کارجو"),
                KeyboardButton(text="خرید اشتراک کارفرما"),
            ]
        )

    # if is_jobseeker_member:
    #     keyboard.append(
    #         [
    #             KeyboardButton(text="خرید اشتراک"),
    #         ]
    #     )

    # if is_company_member:
    #     keyboard.extend(
    #         [
    #             [
    #                 KeyboardButton(text="خرید اشتراک"),
    #             ],
    #         ]
    #     )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
