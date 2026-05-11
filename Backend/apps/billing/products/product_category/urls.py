from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.billing.products.product_category.views import ProductCategoryViewSet


router = DefaultRouter()
router.register(r"", ProductCategoryViewSet, basename="product-category")

urlpatterns = [
    path("", include(router.urls)),
]
