from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(
    is_jobseeker_member: bool = False,
    is_company_member: bool = False,
    is_bot_bale_member: bool = False,
    state: str = "starter",
) -> ReplyKeyboardMarkup:
    keyboard = []

    if not is_bot_bale_member:
        keyboard.append(
            [
                KeyboardButton(text="عضویت در بات")
            ]
        )

        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
        )

    if state == "starter":
        keyboard.append(
            [
                KeyboardButton(text="کارجو"),
                KeyboardButton(text="کارفرما"),
            ]
        )

    elif state == "jobseeker":
        keyboard.extend(
            [
                [
                    KeyboardButton(text="تکمیل رزومه آنلاین"),
                    KeyboardButton(text="آپلود فایل رزومه"),
                ],
                [
                    KeyboardButton(text="بازگشت به منو اصلی"),
                ],
            ]
        )

    elif state == "company":
        keyboard.extend(
            [
                [
                    KeyboardButton(text="ثبت نیازمندی جدید"),
                    KeyboardButton(text="مدیریت آگهی های شغلی"),
                ],
                [
                    KeyboardButton(text="ویرایش پروفایل"),
                ],
                [
                    KeyboardButton(text="بازگشت به منو اصلی"),
                ],
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
