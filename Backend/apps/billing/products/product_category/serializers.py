from rest_framework import serializers

from apps.billing.products.product_category.models import ProductCategory


class ProductCategoryParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "title",
            "slug",
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    parent = ProductCategoryParentSerializer(read_only=True)

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source="parent",
        write_only=True,
        required=False,
        allow_null=True,
    )

    children_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "title",
            "slug",
            "description",

            "parent",
            "parent_id",
            "children_count",

            "is_active",
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

    def get_children_count(self, obj):
        return obj.children.count()

    def validate_parent_id(self, value):
        """
        جلوگیری از اینکه category والد خودش شود.
        """
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError(
                "یک دسته‌بندی نمی‌تواند والد خودش باشد."
            )

        return value
