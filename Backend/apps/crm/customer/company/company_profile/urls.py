from django.urls import path

from .views import (
    CompanyProfileRegisterAPIView,
    MyCompanyProfileDetailsAPIView,
    AdminCompanyProfileListAPIView,
    AdminCompanyProfileDetailAPIView,
    CompanyChoicesAPIView,
    MyCompanyProfileDetailAPIView
)

urlpatterns = [

    # user endpoints
    path(
        "me/",
        MyCompanyProfileDetailsAPIView.as_view(),
        name="company-profile-me",
    ),
    
    path(
    "me/<int:pk>/",
    MyCompanyProfileDetailAPIView.as_view(),
    name="company-profile-me-detail",
    ),


    path(
        "register/",
        CompanyProfileRegisterAPIView.as_view(),
        name="company-profile-create",
    ),
    

    # admin endpoints
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
    
        # admin endpoints
    path(
        "choices/",
        CompanyChoicesAPIView.as_view(),
        name="company-choices-list",
    ),
]
