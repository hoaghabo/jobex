from django.urls import include, path


urlpatterns = [
    path("", include("apps.billing.products.product_profile.urls")),
    path("categories/", include("apps.billing.products.product_category.urls")),
    path("", include("apps.billing.products.product_type.urls")),

]
