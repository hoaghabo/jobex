from django.urls import path, include


app_name = "company"

urlpatterns = [
    path("profile/", include("apps.crm.customer.company.company_profile.urls")),
]
