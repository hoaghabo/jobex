from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.billing.products.product_profile.models import Product
from apps.billing.products.product_profile.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    queryset = Product.objects.select_related(
        "category",
        "product_type",
        "status",
    ).all()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get("category_id")
        product_type_id = self.request.query_params.get("product_type_id")
        status_id = self.request.query_params.get("status_id")
        status_code = self.request.query_params.get("status_code")
        is_active = self.request.query_params.get("is_active")
        is_public = self.request.query_params.get("is_public")
        search = self.request.query_params.get("search")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if product_type_id:
            queryset = queryset.filter(product_type_id=product_type_id)

        if status_id:
            queryset = queryset.filter(status_id=status_id)

        if status_code:
            queryset = queryset.filter(status__code=status_code)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == "true")

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset
