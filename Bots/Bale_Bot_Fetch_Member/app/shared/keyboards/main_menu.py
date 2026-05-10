from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(
    is_jobseeker_member: bool = False,
    is_company_member: bool = False,
    is_bot_bale_member: bool = False,
    state: str = "starter",
) -> ReplyKeyboardMarkup:
    keyboard: list[list[KeyboardButton]] = []

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
        if is_jobseeker_member:
            keyboard.extend(
                [
                    [
                        KeyboardButton(text="مشاهده رزومه"),
                        KeyboardButton(text="ویرایش رزومه"),
                    ],
                    [
                        KeyboardButton(text="فرصت‌های شغلی"),
                    ],
                    [
                        KeyboardButton(text="بازگشت به منو اصلی"),
                    ],
                ]
            )
        else:
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
        if is_company_member:
            keyboard.extend(
                [
                    [
                        KeyboardButton(text="ثبت نیازمندی جدید"),
                    ],
                    [
                        KeyboardButton(text="مدیریت نیازمندی‌ها"),
                    ],
                    [
                        KeyboardButton(text="ویرایش پروفایل شرکت"),
                    ],
                    [
                        KeyboardButton(text="بازگشت به منو اصلی"),
                    ],
                ]
            )
        else:
            keyboard.extend(
                [
                    [
                        KeyboardButton(text="تکمیل پروفایل شرکت"),
                    ],
                    [
                        KeyboardButton(text="بازگشت به منو اصلی"),
                    ],
                ]
            )

    else:
        keyboard.append(
            [
                KeyboardButton(text="بازگشت به منو اصلی"),
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید",
    )
