from django.db import models
from apps.crm.customer.company.company_membership.models import CompanyMembership


class CompanyProfile(models.Model):
    class OrganizationSizeChoices(models.TextChoices):
        FROM_5_TO_50 = "5_50", "۵ تا ۵۰ نفر"
        FROM_50_TO_100 = "50_100", "۵۰ تا ۱۰۰ نفر"
        FROM_200_TO_500 = "200_500", "۲۰۰ تا ۵۰۰ نفر"
        MORE_THAN_500 = "500_plus", "۵۰۰ نفر به بالا"

    class CityChoices(models.TextChoices):
        TEHRAN = "tehran", "تهران"
        ALBORZ = "alborz", "البرز"
        YAZD = "yazd", "یزد"
        AHVAZ = "ahvaz", "اهواز"
        MAZANDARAN = "mazandaran", "مازندران"
        KERMAN = "kerman", "کرمان"
        MASHHAD = "mashhad", "مشهد"
        GILAN = "gilan", "گیلان"
        SHIRAZ = "shiraz", "شیراز"
        TABRIZ = "tabriz", "تبریز"
        QAZVIN = "qazvin", "قزوین"
        OTHER = "other", "سایر"

    company_membership = models.ForeignKey(
        CompanyMembership,
        on_delete=models.CASCADE,
        related_name="company_profiles",
        verbose_name="عضویت شرکت"
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="نام شرکت"
    )

    phone_number = models.CharField(
        max_length=20,
        verbose_name="شماره موبایل"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل"
    )

    organization_size = models.CharField(
        max_length=20,
        choices=OrganizationSizeChoices.choices,
        verbose_name="ابعاد سازمان",
        blank=True,
    )

    city = models.CharField(
        max_length=20,
        choices=CityChoices.choices,
        blank=True,
        verbose_name="شهر"
    )

    industry = models.CharField(
        max_length=255,
        verbose_name="صنعت/حوزه فعالیت سازمان"
    )

    full_address = models.TextField(
        verbose_name="آدرس کامل سازمان"
    )

    website = models.URLField(
        blank=True,
        verbose_name="آدرس وب‌سایت سازمان"
    )

    landline_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تلفن ثابت"
    )

    is_registration_complete = models.BooleanField(
        default=False,
        verbose_name="ثبت‌نام کامل شده"
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
        verbose_name = "پروفایل شرکت"
        verbose_name_plural = "پروفایل شرکت‌ها"

    def check_registration_complete(self):
        required_fields = [
            "company_name",
            "phone_number",
            "email",
            "organization_size",
            "city",
            "industry",
            "full_address",
        ]

        for field_name in required_fields:
            value = getattr(self, field_name, None)

            if value is None:
                return False

            if isinstance(value, str) and not value.strip():
                return False

        return True

    def update_registration_status(self, save=True):
        self.is_registration_complete = self.check_registration_complete()

        if save:
            self.save(update_fields=["is_registration_complete"])

        return self.is_registration_complete

    def __str__(self):
        return self.company_name or self.phone_number
