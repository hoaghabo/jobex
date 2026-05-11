from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.billing.products.product_category.models import ProductCategory
from apps.billing.products.product_category.serializers import ProductCategorySerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer

    queryset = ProductCategory.objects.select_related(
        "parent",
    ).prefetch_related(
        "children",
    ).all()

    def get_permissions(self):
        """
        دیدن دسته‌بندی‌ها برای همه آزاد است.
        ساخت، ویرایش و حذف فقط برای کاربران احراز هویت‌شده.
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()

        parent_id = self.request.query_params.get("parent_id")
        is_active = self.request.query_params.get("is_active")
        search = self.request.query_params.get("search")
        root_only = self.request.query_params.get("root_only")

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        if root_only is not None:
            if root_only.lower() == "true":
                queryset = queryset.filter(parent__isnull=True)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.order_by("sort_order", "id")
