from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.accounts.models import Accounts


class JobSeekerProfile(models.Model):
    class DegreeChoices(models.TextChoices):
        DIPLOMA = "diploma", "دیپلم"
        ASSOCIATE = "associate", "کاردانی"
        BACHELOR = "bachelor", "کارشناسی"
        MASTER = "master", "کارشناسی ارشد"
        PHD = "phd", "دکتری"

    class WorkEnthusiastGroupChoices(models.TextChoices):
        MANAGEMENT = "management", "حوزه مدیریت"
        SALES_MARKETING = "sales_marketing", "حوزه فروش و بازاریابی"
        SUPPORT = "support", "حوزه پشتیبانی"
        DIGITAL = "digital", "حوزه دیجیتال"
        FINANCE_ADMIN = "finance_admin", "حوزه مالی و اداری"
        OTHER = "other", "سایر"

    class SalaryRangeChoices(models.TextChoices):
        FROM_20_TO_30 = "20_30", "۲۰ تا ۳۰ میلیون"
        FROM_30_TO_40 = "30_40", "۳۰ تا ۴۰ میلیون"
        FROM_40_TO_50 = "40_50", "۴۰ تا ۵۰ میلیون"
        FROM_50_TO_60 = "50_60", "۵۰ تا ۶۰ میلیون"
        FROM_60_TO_70 = "60_70", "۶۰ تا ۷۰ میلیون"
        FROM_70_TO_80 = "70_80", "۷۰ تا ۸۰ میلیون"

    class WorkLocationPriorityChoices(models.TextChoices):
        CITY_CENTER = "city_center", "مرکز شهر"
        NORTH = "north", "شمال شهر"
        WEST = "west", "غرب"
        EAST = "east", "شرق"
        SOUTH = "south", "جنوب"
        SUBURB = "suburb", "حومه"

    account = models.OneToOneField(
        Accounts,
        on_delete=models.CASCADE,
        related_name="job_seeker_profile",
        verbose_name="حساب کاربری"
    )

    degree = models.CharField(
        max_length=20,
        choices=DegreeChoices.choices,
        blank=True,
        verbose_name="مدرک تحصیلی"
    )

    work_enthusiasts = ArrayField(
        base_field=models.CharField(
            max_length=30,
            choices=WorkEnthusiastGroupChoices.choices,
        ),
        default=list,
        blank=True,
        verbose_name="علاقه‌مندی‌های شغلی"
    )

    salary_range = models.CharField(
        max_length=10,
        choices=SalaryRangeChoices.choices,
        blank=True,
        verbose_name="بازه حقوق درخواستی"
    )

    work_location_priority = models.CharField(
        max_length=20,
        choices=WorkLocationPriorityChoices.choices,
        blank=True,
        verbose_name="اولویت محل کار"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "پروفایل کارجو"
        verbose_name_plural = "پروفایل کارجویان"

    def __str__(self):
        return f"پروفایل کارجوی {self.account.display_name or self.account.phone_number}"


