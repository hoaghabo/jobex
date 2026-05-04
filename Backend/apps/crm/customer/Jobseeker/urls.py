from django.urls import path, include

urlpatterns = [
    path(
        "profile/",
        include("apps.crm.customer.Jobseeker.jobseeker_profile.urls")
    ),
]
