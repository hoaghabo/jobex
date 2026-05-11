from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class ProductType(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name="عنوان"
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="کد سیستمی",
        help_text="مثلاً: subscription, job_package, campaign_credit"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    requires_fulfillment = models.BooleanField(
        default=True,
        verbose_name="نیازمند فعال‌سازی بعد از خرید"
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
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
        verbose_name = "نوع محصول"
        verbose_name_plural = "انواع محصول"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.code:
            self.code = self.code.lower().strip()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.title)

        self.code = self.code.lower().strip()

        super().save(*args, **kwargs)
