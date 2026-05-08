
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


def normalize_website(url: str) -> str:
    url = url.strip()
    if not url:
        return url

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    return url