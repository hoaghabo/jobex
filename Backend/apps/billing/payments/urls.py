from django.urls import path, include

urlpatterns = [
    path("", include("apps.billing.payments.payment_log.urls")),
]
