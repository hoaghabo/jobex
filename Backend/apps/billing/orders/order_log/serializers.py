from rest_framework import serializers

from apps.billing.orders.order_log.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "payment",
            "gateway",
            "product_id",
            "product_data",
            "amount",
            "currency",
            "status",
            "tracking_code",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "gateway",
            "product_id",
            "amount",
            "currency",
            "status",
            "tracking_code",
            "paid_at",
            "created_at",
        ]
        read_only_fields = fields
