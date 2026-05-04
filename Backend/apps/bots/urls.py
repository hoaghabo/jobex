from django.urls import path
from apps.bots.bale.BaleProfile.views import (
    AdminBaleProfileDetailAPIView,
    AdminBaleProfileListAPIView,
    BaleMyProfileDetailsAPIView,
    BaleRegisterAPIView,
)


app_name = "bots"

urlpatterns = [
    path(
        "admin/bale_profiles/",
        AdminBaleProfileListAPIView.as_view(),
        name="admin_bale_profile_list",
    ),
    
    path(
        "admin/bale_profiles/<int:pk>/",
        AdminBaleProfileDetailAPIView.as_view(),
        name= "admin_bale_profile_detail",
    ),
    
    path(
        "bale_profile/me/",
        BaleMyProfileDetailsAPIView.as_view(),
        name="my_bale_profile",
    ),
    
    path(
        "bale_profile/register/",
        BaleRegisterAPIView.as_view(),
        name="bale_profile_register"
    )
]
