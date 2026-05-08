from django.db import models
from apps.crm.customer.company.company_profile.models import CompanyProfile


class JobPosting(models.Model):
    class DegreeChoices(models.TextChoices):
        BACHELOR = "bachelor", "کارشناسی"
        MASTER = "master", "کارشناسی ارشد"
        PHD = "phd", "دکتری"

    class JobTitleChoices(models.TextChoices):
        SALES_MARKETING_SPECIALIST_MANAGER = (
            "sales_marketing_specialist_manager",
            "فروش و بازاریابی - کارشناس و مدیریت",
        )
        DIRECT_SALES_MARKETER_VISITOR = (
            "direct_sales_marketer_visitor",
            "فروش مستقیم - بازاریاب - ویزیتور",
        )
        CUSTOMER_SERVICE_SUPPORT = (
            "customer_service_support",
            "خدمات و پشتیبانی مشتریان",
        )
        GRAPHIC_MOTION_PHOTOGRAPHY = (
            "graphic_motion_photography",
            "گرافیک - موشن - عکاسی",
        )
        UI_UX_DESIGN = (
            "ui_ux_design",
            "طراحی رابط کاربری (UI-UX)",
        )
        PRODUCT_MANAGER_OWNER = (
            "product_manager_owner",
            "مدیر محصول - مالک محصول",
        )
        SOFTWARE_DEVELOPMENT_PROGRAMMING = (
            "software_development_programming",
            "توسعه نرم افزار و برنامه نویسی",
        )
        NETWORK_HARDWARE_SOFTWARE_SUPPORT = (
            "network_hardware_software_support",
            "شبکه - پشتیبانی سخت افزار یا نرم افزار",
        )
        ARTIFICIAL_INTELLIGENCE = (
            "artificial_intelligence",
            "هوش مصنوعی",
        )
        FINANCE_ACCOUNTING = (
            "finance_accounting",
            "مالی - حسابداری",
        )
        EXECUTIVE_INTERNAL_MANAGER = (
            "executive_internal_manager",
            "مدیر اجرایی و مدیر داخلی",
        )
        OFFICE_ADMIN_EMPLOYEE = (
            "office_admin_employee",
            "مسئول دفتر - کارمند اداری",
        )
        MEDICAL_REPRESENTATIVE = (
            "medical_representative",
            "نماینده علمی/مدرپ",
        )
        HUMAN_RESOURCES = (
            "human_resources",
            "منابع انسانی",
        )
        CONTENT_PRODUCTION = (
            "content_production",
            "تولید محتوا",
        )
        PUBLIC_RELATIONS = (
            "public_relations",
            "روابط عمومی",
        )
        SOCIAL_MEDIA = (
            "social_media",
            "شبکه‌های اجتماعی",
        )
        BUSINESS_STRATEGY_DEVELOPMENT_ANALYSIS = (
            "business_strategy_development_analysis",
            "تحلیل توسعه استراتژی کسب و کار",
        )

    class CooperationTypeChoices(models.TextChoices):
        FULL_TIME = "full_time", "تمام‌وقت"
        PART_TIME = "part_time", "پاره‌وقت"
        REMOTE = "remote", "دورکار"

    class AttendanceTypeChoices(models.TextChoices):
        ON_SITE = "on_site", "مستقر"
        MISSION = "mission", "مأموریت"
        REMOTE = "remote", "دورکار"

    class WorkExperienceChoices(models.TextChoices):
        INTERN = "intern", "کارآموز"
        ONE_TO_THREE_YEARS = "1_to_3_years", "1 تا 3 سال"
        THREE_TO_FIVE_YEARS = "3_to_5_years", "3 تا 5 سال"
        FIVE_TO_SEVEN_YEARS = "5_to_7_years", "5 تا 7 سال"
        MORE_THAN_SEVEN_YEARS = "more_than_7_years", "بیشتر"

    class WorkingDaysChoices(models.TextChoices):
        SATURDAY_TO_WEDNESDAY = "saturday_to_wednesday", "شنبه تا چهارشنبه"
        SATURDAY_TO_THURSDAY = "saturday_to_thursday", "شنبه تا پنجشنبه"
        TOTAL_WORKING_HOURS = "total_working_hours", "مجموع ساعت کار"

    class WorkingHoursChoices(models.TextChoices):
        EIGHT_TO_SIXTEEN = "8_to_16", "8 تا 16"
        NINE_TO_SEVENTEEN = "9_to_17", "9 تا 17"
        OTHER = "other", "سایر"

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="job_postings",
        verbose_name="شرکت"
    )

    job_title = models.CharField(
        max_length=100,
        choices=JobTitleChoices.choices,
        verbose_name="عنوان شغلی",
    )

    cooperation_type = models.CharField(
        max_length=20,
        choices=CooperationTypeChoices.choices,
        verbose_name="نوع همکاری",
    )

    degree = models.CharField(
        max_length=20,
        choices=DegreeChoices.choices,
        blank=True,
        null=True,
    )

    minimum_work_experience = models.CharField(
        max_length=30,
        choices=WorkExperienceChoices.choices,
        verbose_name="حداقل سابقه کاری",
    )

    required_skills = models.TextField(
        verbose_name="مهارت‌های الزامی"
    )

    job_description = models.TextField(
        verbose_name="شرح وظایف شغلی"
    )

    attendance_type = models.CharField(
        max_length=30,
        choices=AttendanceTypeChoices.choices,
        verbose_name="نحوه حضور",
    )

    working_days = models.CharField(
        max_length=40,
        choices=WorkingDaysChoices.choices,
        verbose_name="روزهای کاری",
    )

    has_overtime = models.BooleanField(
        default=False,
        verbose_name="اضافه‌کار دارد؟",
    )

    working_hours = models.CharField(
        max_length=20,
        choices=WorkingHoursChoices.choices,
        verbose_name="ساعات کاری",
    )

    working_hours_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="توضیح ساعات کاری",
    )

    is_salary_negotiable = models.BooleanField(
        default=False,
        verbose_name="حقوق توافقی است؟",
    )

    salary_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="توضیحات حقوق",
    )

    benefits = models.TextField(
        blank=True,
        null=True,
        verbose_name="مزایا",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_job_title_display()

    class Meta:
        verbose_name = "آگهی شغلی"
        verbose_name_plural = "آگهی‌های شغلی"
