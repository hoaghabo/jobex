from rest_framework import serializers

from apps.billing.products.product_type.models import ProductType


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "id",
            "title",
            "code",
            "description",
            "is_active",
            "requires_fulfillment",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ProductTypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "id",
            "title",
            "code",
        ]
