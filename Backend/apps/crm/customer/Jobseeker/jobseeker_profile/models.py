from django.db import models
from apps.accounts.models import Accounts
from django.contrib.postgres.fields import ArrayField

class JobSeekerProfile(models.Model):

    class DegreeChoices(models.TextChoices):
        DIPLOMA = "diploma", "دیپلم"
        ASSOCIATE = "associate", "کاردانی"
        BACHELOR = "bachelor", "کارشناسی"
        MASTER = "master", "کارشناسی ارشد"
        PHD = "phd", "دکتری"

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

    class CampaignRequestChoices(models.TextChoices):
        MESSENGER = "messenger", "ارسال پیام‌رسان (واتساپ، تلگرام، موبایل بله)"
        EMAIL = "email", "ارسال ایمیل"
        SMS = "sms", "ارسال پیامک"
        PUSH_NOTIFICATION = "push_notification", "ارسال پوش نوتیفیکیت"
        JOBEX_CHANNELS = "jobex_channels", "کانال‌های ارتباطی جابکس"
        COMBINED = "combined", "ترکیب (بالاترین بازخورد)"

    account = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False)

    city = models.CharField(
        max_length=20,
        choices=CityChoices.choices,
        blank=True,
        null=True
    )

    day_birthdate = models.IntegerField(null=True, blank=True)
    month_birthdate = models.IntegerField(null=True, blank=True)
    year_birthdate = models.IntegerField(null=True, blank=True)

    degree = models.CharField(
        max_length=20,
        choices=DegreeChoices.choices,
        blank=True,
        null=True
    )

    email = models.EmailField(blank=True, null=True)

    work_enthusiasts = ArrayField(
        models.CharField(
        max_length=30,
        choices=WorkEnthusiastGroupChoices.choices,
        blank=True,
        null=True,
        default=list
    )
    )

    salary_range = models.CharField(
        max_length=10,
        choices=SalaryRangeChoices.choices,
        blank=True,
        null=True
    )

    work_location_priority = models.CharField(
        max_length=20,
        choices=WorkLocationPriorityChoices.choices,
        blank=True,
        null=True
    )

    campaign_request = ArrayField(models.CharField(
        max_length=30,
        choices=CampaignRequestChoices.choices,
        blank=True,
        null=True,
        default=list
    )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
