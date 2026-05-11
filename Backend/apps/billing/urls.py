from django.urls import include, path


urlpatterns = [
    path("products/", include("apps.billing.products.urls")),
    path("payments/", include("apps.billing.payments.urls")),
    path("orders/", include("apps.billing.orders.urls")),
]
