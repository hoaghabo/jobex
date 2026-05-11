from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    title = models.CharField(max_length=150, verbose_name="عنوان")
    slug = models.SlugField(max_length=180, unique=True, verbose_name="اسلاگ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته‌بندی والد"
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی محصولات"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


