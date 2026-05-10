from django.urls import path, include

urlpatterns = [
    path("profile/", include("apps.panel.marketing.campaigns.campaign_profile.urls")),
]
