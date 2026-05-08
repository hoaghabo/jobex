from django.db import models
from apps.accounts.models import Accounts


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

    account = models.OneToOneField(
        Accounts,
        on_delete=models.CASCADE,
        related_name="company_profile"
    )
    fullname = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    organization_size = models.CharField(
        max_length=20,
        choices=OrganizationSizeChoices.choices,
        verbose_name="ابعاد سازمان",
        blank=True,
        null=True,
    )

    city = models.CharField(
        max_length=20,
        choices=CityChoices.choices,
        blank=True,
        null=True,
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
        null=True,
        verbose_name="آدرس وب سایت سازمان"
    )
    landline_phone = models.CharField(
        max_length=20,
        verbose_name="شماره تلفن ثابت"
    )
    
    is_registration_complete = models.BooleanField(
    default=False,
    verbose_name="ثبت‌نام کامل شده"
)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
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
        return self.company_name or self.fullname or str(self.account)

    class Meta:
        verbose_name = "پروفایل شرکت"
        verbose_name_plural = "پروفایل شرکت‌ها"
