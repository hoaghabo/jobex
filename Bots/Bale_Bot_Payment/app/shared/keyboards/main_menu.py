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

    if not is_jobseeker_member and not is_company_member:
        keyboard.append(
            [
                KeyboardButton(text="کارجو"),
                KeyboardButton(text="کارفرما"),
            ]
        )

    if is_jobseeker_member:
        keyboard.append(
            [
                KeyboardButton(text="تکمیل رزومه آنلاین"),
                KeyboardButton(text="آپلود فایل رزومه"),
            ]
        )

    if is_company_member:
        keyboard.extend(
            [
                [
                    KeyboardButton(text="ثبت نیازمندی جدید"),
                    KeyboardButton(text="مدیریت آگهی های شغلی"),
                ],
                [
                    KeyboardButton(text="ویرایش پروفایل"),
                ],
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
