from django.urls import path
from .views import (
    CompanyRoleListCreateAPIView,
    CompanyRoleDetailAPIView
)

urlpatterns = [
    path(
        "company-roles/",
        CompanyRoleListCreateAPIView.as_view(),
        name="company-role-list-create",
    ),
    path(
        "company-roles/<int:pk>/",
        CompanyRoleDetailAPIView.as_view(),
        name="company-role-detail",
    ),
]
