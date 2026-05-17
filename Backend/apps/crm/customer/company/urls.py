from django.urls import path, include


app_name = "company"

urlpatterns = [
    path("profile/", include("apps.crm.customer.company.company_profile.urls")),
    path("jobpost/", include("apps.crm.customer.company.job_posts.urls")),
    path("membership/", include("apps.crm.customer.company.company_membership.urls")),
]
