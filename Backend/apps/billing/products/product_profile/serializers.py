from rest_framework import serializers

from apps.billing.products.product_profile.models import Product
from apps.billing.products.product_category.models import ProductCategory
from apps.billing.products.product_type.models import ProductType
from apps.billing.products.product_status.models import ProductStatus


class ProductCategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "title",
            "slug",
        ]


class ProductTypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "id",
            "title",
            "code",
        ]


class ProductStatusShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = [
            "id",
            "title",
            "code",
            "is_public",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategoryShortSerializer(read_only=True)
    product_type = ProductTypeShortSerializer(read_only=True)
    status = ProductStatusShortSerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=ProductCategory.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type",
        queryset=ProductType.objects.all(),
        write_only=True,
    )

    status_id = serializers.PrimaryKeyRelatedField(
        source="status",
        queryset=ProductStatus.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",

            "category",
            "category_id",

            "product_type",
            "product_type_id",

            "status",
            "status_id",

            "title",
            "slug",
            "short_description",
            "description",
            "base_price",
            "sku",

            "is_active",
            "is_public",
            "sort_order",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]
