from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    category = models.ForeignKey(
        "billing.ProductCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="دسته‌بندی"
    )

    product_type = models.ForeignKey(
        "billing.ProductType",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="نوع محصول"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان"
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name="اسلاگ"
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="توضیح کوتاه"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات کامل"
    )

    status = models.ForeignKey(
        "billing.ProductStatus",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="وضعیت"
    )


    base_price = models.BigIntegerField(
        default=0,
        verbose_name="قیمت پایه"
    )

    sku = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="کد محصول"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    is_public = models.BooleanField(
        default=True,
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
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)
