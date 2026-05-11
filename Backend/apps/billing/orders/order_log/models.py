from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.billing.payments.payment_log.models import Payment


class OrderManager(models.Manager):
    @transaction.atomic
    def get_or_create_from_payment(self, payment):
        if payment.status != Payment.Status.PAID:
            raise ValueError("امکان ساخت سفارش از پرداخت ناموفق وجود ندارد.")

        tracking_code = f"ORD-{timezone.now().strftime('%Y%m%d')}-{get_random_string(8).upper()}"

        order, created = self.get_or_create(
            payment=payment,
            defaults={
                "user": payment.user,
                "gateway": payment.gateway,
                "product_id": payment.product_id,
                "product_data": payment.product_data,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": Order.Status.PAID,
                "tracking_code": tracking_code,
                "paid_at": payment.paid_at or timezone.now(),
            },
        )

        return order, created


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        PAID = "paid", "پرداخت شده"
        CANCELED = "canceled", "لغو شده"
        REFUNDED = "refunded", "مرجوع شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_orders",
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="order",
    )

    gateway = models.CharField(max_length=32, db_index=True)

    product_id = models.CharField(max_length=128, db_index=True)
    product_data = models.JSONField(default=dict, blank=True)

    amount = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=16, default="IRR")

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    tracking_code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["product_id"]),
            models.Index(fields=["tracking_code"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.tracking_code}"
