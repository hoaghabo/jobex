from django.urls import include, path


urlpatterns = [
    path("logs/", include("apps.billing.orders.order_log.urls")),
]
