
from .api import get_choices_items


def normalize_digits(value: str) -> str:
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"

    translation_table = str.maketrans(
        persian_digits + arabic_digits,
        english_digits + english_digits
    )

    return value.translate(translation_table)


async def get_choice_label(choice_key: str, value: str) -> str:
    if value is None:
        return "-"

    choices = await get_choices_items(choice_key)

    for item in choices:
        if str(item.get("value")) == str(value):
            return item.get("label", value)

    return value


def extract_phone_number(status: dict) -> str | None:
    return (
        status.get("phone_number")
        or status.get("phone")
        or status.get("mobile")
        or status.get("user", {}).get("phone_number")
        or status.get("user", {}).get("phone")
        or status.get("user", {}).get("mobile")
    )


def extract_jobseeker_profile_flags(profile_data: dict | None) -> dict:
    if not profile_data:
        return {}

    result = {}

    for key, value in profile_data.items():
        if isinstance(value, str):
            result[key] = bool(value.strip())
        elif isinstance(value, (list, dict, set, tuple)):
            result[key] = len(value) > 0
        else:
            result[key] = value is not None

    return result


def format_jobseeker_profile_text(jobseeker_profile: dict) -> str:
    profile_id = jobseeker_profile.get("id", "—")

    degree = (
        jobseeker_profile.get("degree_display")
        or jobseeker_profile.get("degree")
        or "ثبت نشده"
    )

    work_enthusiasts = (
        jobseeker_profile.get("work_enthusiasts_display")
        or jobseeker_profile.get("work_enthusiasts")
        or []
    )

    salary_range = (
        jobseeker_profile.get("salary_range_display")
        or jobseeker_profile.get("salary_range")
        or "ثبت نشده"
    )

    work_location_priority = (
        jobseeker_profile.get("work_location_priority_display")
        or jobseeker_profile.get("work_location_priority")
        or "ثبت نشده"
    )

    if isinstance(work_enthusiasts, list):
        work_enthusiasts_text = "، ".join(work_enthusiasts) if work_enthusiasts else "ثبت نشده"
    else:
        work_enthusiasts_text = str(work_enthusiasts) if work_enthusiasts else "ثبت نشده"

    return f"""
🌟 اطلاعات فعلی رزومه شما

🆔 آیدی پروفایل: {profile_id}
🎓 مقطع تحصیلی: {degree}
💼 علاقه‌مندی‌های شغلی: {work_enthusiasts_text}
💰 بازه حقوق: {salary_range}
📍 اولویت محل کار: {work_location_priority}

━━━━━━━━━━━━━━
✨ کارجوی عزیز، لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
""".strip()
