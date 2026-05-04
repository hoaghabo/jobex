from django.urls import path

from .views import (
    CompanyProfileRegisterAPIView,
    MyCompanyProfileDetailsAPIView,
    AdminCompanyProfileListAPIView,
    AdminCompanyProfileDetailAPIView,
)

urlpatterns = [
    path(
        "me/",
        MyCompanyProfileDetailsAPIView.as_view(),
        name="company-profile-me",
    ),
    path(
        "",
        CompanyProfileRegisterAPIView.as_view(),
        name="company-profile-create",
    ),
    path(
        "admin/",
        AdminCompanyProfileListAPIView.as_view(),
        name="admin-company-profile-list",
    ),
    path(
        "admin/<int:pk>/",
        AdminCompanyProfileDetailAPIView.as_view(),
        name="admin-company-profile-detail",
    ),
]
