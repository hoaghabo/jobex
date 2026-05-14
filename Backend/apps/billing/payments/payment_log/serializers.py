from rest_framework import serializers

from apps.billing.payments.payment_log.models import Payment
from apps.billing.orders.order_log.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "gateway",
            "status",
            "manual_review_status",

            "product_id",
            "product_data",

            "amount",
            "currency",
            "description",

            "trackId",
            "payment_url",
            "ref_id",
            "card_pan",
            "fee_type",
            "fee",

            "destination_card_number",
            "destination_card_owner",
            "receipt_image",
            "receipt_file_id",
            "receipt_tracking_code",

            "review_note",
            "reviewed_by",
            "reviewed_at",

            "wallet_transaction_id",
            "wallet_payload",

            "paid_at",
            "created_at",
            "updated_at",

            "order",
        ]
        read_only_fields = fields

    def get_order(self, obj):
        order = getattr(obj, "order", None)

        if not order:
            return None

        return OrderSerializer(order).data


class CreatePaymentSerializer(serializers.Serializer):
    gateway = serializers.ChoiceField(choices=Payment.Gateway.choices)
    product_id = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.IntegerField(required=False, allow_null=True)

    # ZIBAL optional fields
    mobile = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    
    chat_id = serializers.CharField(required=False, allow_blank=True)


class CreatePaymentResponseSerializer(serializers.ModelSerializer):
    card_to_card = serializers.SerializerMethodField()
    bale_wallet = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "gateway",
            "status",
            "manual_review_status",
            "amount",
            "currency",
            "product_id",
            "product_data",
            "trackId",
            "payment_url",
            "card_to_card",
            "bale_wallet",
            "created_at",
        ]
        read_only_fields = fields

    def get_card_to_card(self, obj):
        if obj.gateway != Payment.Gateway.CARD_TO_CARD:
            return None

        return {
            "destination_card_number": obj.destination_card_number,
            "destination_card_owner": obj.destination_card_owner,
            "message": "بعد از واریز مبلغ، رسید پرداخت را ارسال کنید.",
        }

    def get_bale_wallet(self, obj):
        if obj.gateway != Payment.Gateway.BALE_WALLET:
            return None

        wallet_payload = obj.wallet_payload or {}
        message_id = wallet_payload.get("message_id")
        
        if message_id:
            return {
                "message_id": message_id,
                "invoice_sent": True,
                "message": "فاکتور پرداخت برای شما ارسال شد.",
            }
        else:
            return {
                "message_id": None,
                "invoice_sent": False,
                "message": "خطا در ارسال فاکتور پرداخت.",
            }


class ZibalCallbackSerializer(serializers.Serializer):
    trackId = serializers.CharField()
    Status = serializers.CharField()


class SubmitCardToCardReceiptSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    receipt_image = serializers.FileField(required=False)
    receipt_file_id = serializers.CharField(required=False, allow_blank=True)
    receipt_tracking_code = serializers.CharField(required=False, allow_blank=True)

    source = serializers.CharField(required=False, allow_blank=True)
    message_id = serializers.CharField(required=False, allow_blank=True)
    chat_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("receipt_image") and not attrs.get("receipt_file_id"):
            raise serializers.ValidationError({
                "receipt": "یکی از receipt_image یا receipt_file_id الزامی است."
            })

        return attrs


class ApproveCardToCardPaymentSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    review_note = serializers.CharField(required=False, allow_blank=True)
    ref_id = serializers.CharField(required=False, allow_blank=True)


class RejectCardToCardPaymentSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    review_note = serializers.CharField(required=False, allow_blank=True)


class ConfirmBaleWalletPaymentSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField(required=False, allow_null=True)
    telegram_payment_charge_id = serializers.CharField(required=True, max_length=255)
    provider_payment_charge_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    invoice_payload = serializers.CharField(required=True, max_length=128)
    chat_id = serializers.CharField(required=False, allow_blank=True)
    message_id = serializers.IntegerField(required=False, allow_null=True)



class PaymentStatusSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    is_successful = serializers.SerializerMethodField()
    is_pending = serializers.SerializerMethodField()
    is_failed = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "gateway",
            "status",
            "status_display",
            "manual_review_status",

            "product_id",
            "product_data",
            "product_name",
            "product_description",

            "amount",
            "currency",

            "trackId",
            "payment_url",
            "ref_id",

            "receipt_tracking_code",
            "receipt_file_id",

            "wallet_transaction_id",
            "wallet_payload",

            "paid_at",
            "created_at",
            "updated_at",

            "is_successful",
            "is_pending",
            "is_failed",

            "order",
        ]
        read_only_fields = fields

    def get_order(self, obj):
        order = getattr(obj, "order", None)
        if not order:
            return None

        return {
            "id": order.id,
            "status": order.status,
            "tracking_code": order.tracking_code,
            "paid_at": order.paid_at,
            "created_at": order.created_at,
        }

    def get_product_name(self, obj):
        product_data = obj.product_data or {}

        # اول از product_data بخوان
        name = (
            product_data.get("name")
            or product_data.get("title")
            or product_data.get("product_name")
        )
        if name:
            return name

        # اگر relation به product داری، از خود مدل بخوان
        product = getattr(obj, "product", None)
        if product:
            return getattr(product, "name", None) or getattr(product, "title", None)

        return "محصول خریداری‌شده"

    def get_product_description(self, obj):
        product_data = obj.product_data or {}

        description = (
            product_data.get("description")
            or product_data.get("caption")
            or product_data.get("product_description")
            or ""
        )
        if description:
            return description

        product = getattr(obj, "product", None)
        if product:
            return getattr(product, "description", "") or ""

        return ""

    def get_status_display(self, obj):
        status_map = {
            "pending": "در انتظار پرداخت",
            "completed": "پرداخت موفق",
            "failed": "پرداخت ناموفق",
            "cancelled": "لغو شده",
            "awaiting_verification": "در انتظار بررسی",
            "paid": "پرداخت شده",
        }
        return status_map.get(obj.status, obj.status)

    def get_is_successful(self, obj):
        return obj.status in ["completed", "paid"]

    def get_is_pending(self, obj):
        return obj.status in ["pending", "awaiting_verification"]

    def get_is_failed(self, obj):
        return obj.status in ["failed", "cancelled"]