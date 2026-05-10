from django.urls import path, include

urlpatterns = [
    path("marketing/", include("apps.panel.marketing.urls")),
]
