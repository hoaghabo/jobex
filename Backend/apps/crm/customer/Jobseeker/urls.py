from django.urls import path, include

urlpatterns = [
    path(
        "profile/",
        include("apps.crm.customer.Jobseeker.jobseeker_profile.urls")
    ),
    path(
        "applications/",
        include("apps.crm.customer.Jobseeker.jobs_application.urls")
    )
]
