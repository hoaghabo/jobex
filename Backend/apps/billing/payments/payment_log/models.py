from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class Payment(models.Model):
    class Gateway(models.TextChoices):
        ZARINPAL = "zarinpal", "زرین‌پال"
        CARD_TO_CARD = "card_to_card", "کارت به کارت"
        BALE_WALLET = "bale_wallet", "کیف پول بله"

    class Status(models.TextChoices):
        INIT = "init", "ایجاد اولیه"
        PENDING = "pending", "در انتظار پرداخت"
        WAITING_FOR_RECEIPT = "waiting_for_receipt", "در انتظار رسید"
        WAITING_FOR_REVIEW = "waiting_for_review", "در انتظار بررسی"
        PAID = "paid", "پرداخت شده"
        FAILED = "failed", "ناموفق"
        CANCELED = "canceled", "لغو شده"
        REJECTED = "rejected", "رد شده"

    class ManualReviewStatus(models.TextChoices):
        NONE = "none", "بدون بررسی"
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payments",
    )

    gateway = models.CharField(
        max_length=32,
        choices=Gateway.choices,
        db_index=True,
    )

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.INIT,
        db_index=True,
    )

    manual_review_status = models.CharField(
        max_length=32,
        choices=ManualReviewStatus.choices,
        default=ManualReviewStatus.NONE,
        db_index=True,
    )

    product_id = models.CharField(max_length=128, db_index=True)
    product_data = models.JSONField(default=dict, blank=True)

    amount = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=16, default="IRR")
    description = models.TextField(blank=True)

    # Zarinpal
    authority = models.CharField(max_length=255, blank=True, db_index=True)
    payment_url = models.URLField(max_length=1000, blank=True)
    ref_id = models.CharField(max_length=255, blank=True, db_index=True)
    card_pan = models.CharField(max_length=64, blank=True)
    fee_type = models.CharField(max_length=64, blank=True)
    fee = models.PositiveBigIntegerField(null=True, blank=True)

    # Card to card
    destination_card_number = models.CharField(max_length=32, blank=True)
    destination_card_owner = models.CharField(max_length=255, blank=True)

    receipt_image = models.FileField(
        upload_to="billing/card_to_card_receipts/",
        null=True,
        blank=True,
    )
    receipt_file_id = models.CharField(max_length=255, blank=True)
    receipt_tracking_code = models.CharField(max_length=255, blank=True)

    review_note = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_billing_payments",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Bale wallet
    wallet_transaction_id = models.CharField(max_length=255, blank=True, db_index=True)
    wallet_user_id = models.CharField(max_length=255, blank=True)
    wallet_payload = models.JSONField(default=dict, blank=True)

    # Raw payloads
    request_payload = models.JSONField(default=dict, blank=True)
    request_response = models.JSONField(default=dict, blank=True)

    callback_payload = models.JSONField(default=dict, blank=True)

    verify_payload = models.JSONField(default=dict, blank=True)
    verify_response = models.JSONField(default=dict, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["gateway", "status"]),
            models.Index(fields=["product_id"]),
            models.Index(fields=["authority"]),
            models.Index(fields=["ref_id"]),
            models.Index(fields=["wallet_transaction_id"]),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.gateway} - {self.status} - {self.amount}"

    @property
    def is_paid(self):
        return self.status == self.Status.PAID

    def mark_paid(self, ref_id="", extra_data=None, save=True):
        self.status = self.Status.PAID
        self.paid_at = self.paid_at or timezone.now()

        if ref_id:
            self.ref_id = str(ref_id)

        if extra_data:
            current_data = self.verify_response or {}
            current_data.update(extra_data)
            self.verify_response = current_data

        if save:
            self.save(update_fields=[
                "status",
                "paid_at",
                "ref_id",
                "verify_response",
                "updated_at",
            ])

        return self

    def mark_failed(self, extra_data=None, save=True):
        self.status = self.Status.FAILED

        if extra_data:
            current_data = self.verify_response or {}
            current_data.update(extra_data)
            self.verify_response = current_data

        if save:
            self.save(update_fields=[
                "status",
                "verify_response",
                "updated_at",
            ])

        return self

    def submit_card_to_card_receipt(
        self,
        receipt_image=None,
        receipt_file_id="",
        receipt_tracking_code="",
        extra_payload=None,
    ):
        if self.gateway != self.Gateway.CARD_TO_CARD:
            raise ValueError("این پرداخت از نوع کارت به کارت نیست.")

        if self.status not in [
            self.Status.WAITING_FOR_RECEIPT,
            self.Status.WAITING_FOR_REVIEW,
        ]:
            raise ValueError("این پرداخت در وضعیت مناسب برای ارسال رسید نیست.")

        if receipt_image:
            self.receipt_image = receipt_image

        if receipt_file_id:
            self.receipt_file_id = receipt_file_id

        if receipt_tracking_code:
            self.receipt_tracking_code = receipt_tracking_code

        self.status = self.Status.WAITING_FOR_REVIEW
        self.manual_review_status = self.ManualReviewStatus.PENDING

        if extra_payload:
            current_payload = self.request_payload or {}
            current_payload["receipt_submit"] = extra_payload
            self.request_payload = current_payload

        self.save(update_fields=[
            "receipt_image",
            "receipt_file_id",
            "receipt_tracking_code",
            "status",
            "manual_review_status",
            "request_payload",
            "updated_at",
        ])

        return self

    @transaction.atomic
    def approve_manual_payment(self, reviewed_by=None, review_note="", ref_id=""):
        if self.gateway != self.Gateway.CARD_TO_CARD:
            raise ValueError("این پرداخت از نوع کارت به کارت نیست.")

        if self.status != self.Status.WAITING_FOR_REVIEW:
            raise ValueError("این پرداخت در انتظار بررسی نیست.")

        self.status = self.Status.PAID
        self.manual_review_status = self.ManualReviewStatus.APPROVED
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.review_note = review_note or ""
        self.paid_at = self.paid_at or timezone.now()

        if ref_id:
            self.ref_id = ref_id

        self.save(update_fields=[
            "status",
            "manual_review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
            "paid_at",
            "ref_id",
            "updated_at",
        ])

        from apps.billing.orders.models import Order

        order, created = Order.objects.get_or_create_from_payment(self)
        return order

    def reject_manual_payment(self, reviewed_by=None, review_note=""):
        if self.gateway != self.Gateway.CARD_TO_CARD:
            raise ValueError("این پرداخت از نوع کارت به کارت نیست.")

        self.status = self.Status.REJECTED
        self.manual_review_status = self.ManualReviewStatus.REJECTED
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.review_note = review_note or ""

        self.save(update_fields=[
            "status",
            "manual_review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
            "updated_at",
        ])

        return self
