from django.db import models


class Campaign(models.Model):
    class ChannelChoices(models.TextChoices):
        SMS = "sms", "پیامک"
        EMAIL = "email", "ایمیل"
        TELEGRAM = "telegram", "تلگرام"
        WHATSAPP = "whatsapp", "واتساپ"

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "فعال"
        PENDING = "pending", "پیش‌نویس"
        PAUSED = "paused", "متوقف"
        COMPLETED = "completed", "تکمیل‌شده"
        FAILED = "failed", "ناموفق"

    title = models.CharField(max_length=255, verbose_name="عنوان کمپین")

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="وضعیت"
    )
    
    owner = models.ForeignKey(Account)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "کمپین"
        verbose_name_plural = "کمپین‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
