from datetime import datetime, date
from typing import Any
import jdatetime


EN_DIGITS = "0123456789"
FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"

TO_FA_TRANS = str.maketrans(EN_DIGITS, FA_DIGITS)
TO_EN_TRANS = str.maketrans(FA_DIGITS + AR_DIGITS, EN_DIGITS + EN_DIGITS)

JALALI_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]


def fa_digits(value: Any) -> str:
    if value is None:
        return ""
    return str(value).translate(TO_FA_TRANS)


def normalize_digits_to_en(value: Any) -> str:
    return str(value).translate(TO_EN_TRANS)


def format_jalali_date_fa(value: Any) -> str:
    """
    ورودی:
        "2026-05-02"
        "۲۰۲۶-۰۵-۰۲"
        "2026-05-02T10:30:00Z"
        datetime.date
        datetime.datetime

    خروجی:
        "۱۲ اردیبهشت ۱۴۰۵"
    """

    if not value:
        return "نامشخص"

    try:
        if isinstance(value, datetime):
            gregorian_date = value.date()

        elif isinstance(value, date):
            gregorian_date = value

        else:
            value_str = normalize_digits_to_en(value).strip()

            # اگر تاریخ با / آمده بود
            value_str = value_str.replace("/", "-")

            # اگر datetime ISO بود، مثل:
            # 2026-05-02T10:30:00Z
            value_str = value_str.replace("Z", "+00:00")

            if "T" in value_str:
                gregorian_date = datetime.fromisoformat(value_str).date()
            else:
                gregorian_date = datetime.strptime(value_str, "%Y-%m-%d").date()

        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

        day = fa_digits(jalali_date.day)
        month = JALALI_MONTHS[jalali_date.month - 1]
        year = fa_digits(jalali_date.year)

        return f"{day} {month} {year}"

    except Exception:
        return fa_digits(value)
