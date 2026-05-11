from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAdminUser

from apps.billing.products.product_type.models import ProductType
from apps.billing.products.product_type.serializers import ProductTypeSerializer


class ProductTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ProductTypeSerializer

    queryset = ProductType.objects.all().order_by(
        "sort_order",
        "id",
    )

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "title",
        "code",
        "description",
    ]

    ordering_fields = [
        "id",
        "title",
        "code",
        "sort_order",
        "is_active",
        "requires_fulfillment",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "sort_order",
        "id",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.query_params.get("is_active")
        requires_fulfillment = self.request.query_params.get("requires_fulfillment")
        code = self.request.query_params.get("code")

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        if requires_fulfillment is not None:
            queryset = queryset.filter(
                requires_fulfillment=requires_fulfillment.lower() == "true"
            )

        if code:
            queryset = queryset.filter(code=code)

        return queryset
