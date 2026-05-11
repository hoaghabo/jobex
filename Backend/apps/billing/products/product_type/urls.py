from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.billing.products.product_type.views import ProductTypeViewSet


router = DefaultRouter()

router.register(
    r"product-types",
    ProductTypeViewSet,
    basename="product-type",
)

urlpatterns = [
    path("", include(router.urls)),
]
