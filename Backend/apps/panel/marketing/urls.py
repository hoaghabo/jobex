from django.urls import path, include

urlpatterns = [
    path("campaigns/", include("apps.panel.marketing.campaigns.urls")),
]