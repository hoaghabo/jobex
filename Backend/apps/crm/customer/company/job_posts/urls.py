from django.urls import path

from apps.crm.customer.company.job_posts.views import (
    AdminJobPostingListCreateAPIView,
    AdminJobPostingDetailAPIView,
    MyCompanyJobPostingListCreateAPIView,
    MyCompanyJobPostingDetailAPIView,
    JobPostingChoicesAPIView,
)

urlpatterns = [
    path(
        "choices/",
        JobPostingChoicesAPIView.as_view(),
        name="job-posting-choices",
    ),

    path(
        "admin/job-posts/",
        AdminJobPostingListCreateAPIView.as_view(),
        name="admin-job-posting-list-create",
    ),
    path(
        "admin/job-posts/<int:pk>/",
        AdminJobPostingDetailAPIView.as_view(),
        name="admin-job-posting-detail",
    ),

    path(
        "me/",
        MyCompanyJobPostingListCreateAPIView.as_view(),
        name="my-company-job-posting-list-create",
    ),
    path(
        "<int:pk>/",
        MyCompanyJobPostingDetailAPIView.as_view(),
        name="my-company-job-posting-detail",
    ),
]
