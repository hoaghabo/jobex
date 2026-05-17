from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, JobSeekerCampaignChannelCreateView,JobSeekerCampaignRequestListView

router = DefaultRouter()
router.register(r"campaign", CampaignViewSet, basename="campaign")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "campaign-channel/ask/",
        JobSeekerCampaignChannelCreateView.as_view(),
        name="campaign-channel-ask"
    ),
    path(
    "campaign-channel/my-requests/",
    JobSeekerCampaignRequestListView.as_view()
),
]
