from django.urls import path

from .views import (
    JobseekerRegisterAPIView,
    MyJobseekerDetailsAPIView,
    AdminJobseekerProfileListAPIView,
    AdminJobseekerProfileDetailAPIView,
    JobSeekerChoicesAPIView,
)

urlpatterns = [
    path(
        "me/",
        MyJobseekerDetailsAPIView.as_view(),
        name="jobseeker-profile-me",
    ),
    path(
        "",
        JobseekerRegisterAPIView.as_view(),
        name="jobseeker-profile-create",
    ),
    path(
        "admin/",
        AdminJobseekerProfileListAPIView.as_view(),
        name="admin-jobseeker-profile-list",
    ),
    path(
        "admin/<int:pk>/",
        AdminJobseekerProfileDetailAPIView.as_view(),
        name="admin-jobseeker-profile-detail",
    ),
    path("choices/", JobSeekerChoicesAPIView.as_view(), name="jobseeker-choices"),
]
