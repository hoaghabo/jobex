from typing import Any, Dict
from datetime import datetime
from zoneinfo import ZoneInfo
import jdatetime


def _get_display_value(
    data: Dict[str, Any],
    display_key: str,
    raw_key: str,
    default: str = "—"
) -> str:
    """
    اول مقدار display را برمی‌گرداند،
    اگر نبود مقدار raw را،
    و در نهایت default.
    """
    return str(data.get(display_key) or data.get(raw_key) or default)


def format_datetime_jalali(value: str | None) -> str:
    if not value:
        return "—"

    try:
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        tehran_dt = dt.astimezone(ZoneInfo("Asia/Tehran"))
        jalali_dt = jdatetime.datetime.fromgregorian(datetime=tehran_dt)

        return jalali_dt.strftime("%Y/%m/%d - %H:%M")

    except Exception as e:
        print("format_datetime_jalali error:", e)
        return str(value)


def format_jobpost_detail_text(jobpost: Dict[str, Any]) -> str:
    company_name = jobpost.get("company_name") or "—"

    job_title = _get_display_value(
        jobpost,
        "job_title_display",
        "job_title"
    )

    cooperation_type = _get_display_value(
        jobpost,
        "cooperation_type_display",
        "cooperation_type"
    )

    degree = _get_display_value(
        jobpost,
        "degree_display",
        "degree"
    )

    minimum_work_experience = _get_display_value(
        jobpost,
        "minimum_work_experience_display",
        "minimum_work_experience"
    )

    attendance_type = _get_display_value(
        jobpost,
        "attendance_type_display",
        "attendance_type"
    )

    working_days = _get_display_value(
        jobpost,
        "working_days_display",
        "working_days"
    )

    working_hours = _get_display_value(
        jobpost,
        "working_hours_display",
        "working_hours"
    )

    required_skills = jobpost.get("required_skills") or "—"
    job_description = jobpost.get("job_description") or "—"
    has_overtime = "دارد" if jobpost.get("has_overtime") else "ندارد"
    working_hours_description = jobpost.get("working_hours_description") or "—"
    is_salary_negotiable = "بله" if jobpost.get("is_salary_negotiable") else "خیر"
    salary_description = jobpost.get("salary_description") or "—"
    benefits = jobpost.get("benefits") or "—"

    created_at = format_datetime_jalali(jobpost.get("created_at"))
    jobpost_id = jobpost.get("id") or "—"

    text = (
        f"📌 جزئیات آگهی شغلی\n\n"
        f"🏢 شرکت: {company_name}\n"
        f"💼 عنوان شغلی: {job_title}\n"
        f"🤝 نوع همکاری: {cooperation_type}\n"
        f"🎓 مدرک تحصیلی: {degree}\n"
        f"🧠 سابقه کار: {minimum_work_experience}\n"
        f"🛠 مهارت‌های موردنیاز: {required_skills}\n\n"
        f"📝 شرح شغل:\n{job_description}\n\n"
        f"📍 نوع حضور: {attendance_type}\n"
        f"📅 روزهای کاری: {working_days}\n"
        f"⏰ ساعات کاری: {working_hours}\n"
        f"ℹ️ توضیحات ساعات کاری: {working_hours_description}\n"
        f"🕓 اضافه‌کاری: {has_overtime}\n\n"
        f"💰 حقوق توافقی: {is_salary_negotiable}\n"
        f"💵 حقوق: {salary_description}\n"
        f"🎁 مزایا: {benefits}\n\n"
        f"🆔 شناسه آگهی: {jobpost_id}\n"
        f"🕒 تاریخ ایجاد: {created_at}"
    )

    return text
