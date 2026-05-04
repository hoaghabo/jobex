from django.urls import path, include


app_name = "company"

urlpatterns = [
    path("jobseeker/", include("apps.crm.customer.Jobseeker.urls")),
    path("company/", include("apps.crm.customer.company.urls")),
]
