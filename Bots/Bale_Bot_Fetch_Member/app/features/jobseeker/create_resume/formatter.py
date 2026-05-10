
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
