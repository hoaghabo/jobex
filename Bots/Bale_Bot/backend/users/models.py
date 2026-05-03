from django.db import models
from django.utils import timezone


class BotUser(models.Model):
    bale_user_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name="شناسه کاربر در بله",
    )

    chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شناسه چت",
    )

    first_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام در بله",
    )

    last_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام خانوادگی در بله",
    )

    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="نام کاربری",
    )

    phone_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شماره موبایل",
    )

    registered_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام واردشده در ثبت‌نام",
    )

    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="سن",
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شهر",
    )

    is_registered = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="ثبت‌نام کامل شده؟",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال است؟",
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name="ادمین است؟",
    )

    is_blocked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="مسدود شده؟",
    )

    last_state = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="آخرین وضعیت",
    )

    state_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="داده‌های وضعیت",
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="آخرین بازدید",
    )

    registered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تکمیل ثبت‌نام",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="زمان بروزرسانی",
    )

    class Meta:
        verbose_name = "کاربر ربات"
        verbose_name_plural = "کاربران ربات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["bale_user_id"]),
            models.Index(fields=["chat_id"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_registered"]),
            models.Index(fields=["last_seen_at"]),
        ]

    def __str__(self):
        return str(
            self.registered_full_name
            or self.first_name
            or self.username
            or self.bale_user_id
        )

    def mark_seen(self):
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at", "updated_at"])

    def complete_registration(
        self,
        full_name: str,
        phone_number: str,
        age: int,
        city: str,
    ):
        self.registered_full_name = full_name
        self.phone_number = phone_number
        self.age = age
        self.city = city
        self.is_registered = True
        self.registered_at = timezone.now()
        self.last_state = None
        self.state_data = {}
        self.save(
            update_fields=[
                "registered_full_name",
                "phone_number",
                "age",
                "city",
                "is_registered",
                "registered_at",
                "last_state",
                "state_data",
                "updated_at",
            ]
        )
