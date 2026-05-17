from django.db import models
from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile

class CampaignChannel(models.Model):
    key = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کلید"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
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
        verbose_name = "کانال اطلاع‌رسانی"
        verbose_name_plural = "کانال‌های اطلاع‌رسانی"

    def __str__(self):
        return self.title


class JobSeekerProfileCampaignChannel(models.Model):

    class Status(models.TextChoices):
        USER_REQUEST = "user_request", "درخواست کاربر"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"
        SENT = "sent", "ارسال شده"

    job_seeker_profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="profile_campaign_channels",
        verbose_name="پروفایل کارجو"
    )

    campaign_channel = models.ForeignKey(
        CampaignChannel,
        on_delete=models.CASCADE,
        related_name="job_seeker_profile_links",
        verbose_name="کانال اطلاع‌رسانی"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.USER_REQUEST,
        verbose_name="وضعیت درخواست"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "کانال اطلاع‌رسانی پروفایل کارجو"
        verbose_name_plural = "کانال‌های اطلاع‌رسانی پروفایل‌های کارجو"
        unique_together = ("job_seeker_profile", "campaign_channel", "status")

    def __str__(self):
        return f"{self.job_seeker_profile} - {self.campaign_channel} - {self.status}"

