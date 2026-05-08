from django.urls import path, include

urlpatterns = [
    path(
        "customer/",
        include("apps.crm.customer.urls")
    ),
]
