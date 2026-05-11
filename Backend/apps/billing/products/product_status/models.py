from django.db import models
from django.utils.text import slugify


class ProductStatus(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="عنوان"
    )

    code = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="کد سیستمی",
        help_text="مثلاً: draft, active, inactive, archived"
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

    is_public = models.BooleanField(
        default=False,
        verbose_name="قابل نمایش عمومی"
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
        verbose_name = "وضعیت محصول"
        verbose_name_plural = "وضعیت‌های محصول"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.title)

        self.code = self.code.lower().strip()
        super().save(*args, **kwargs)
