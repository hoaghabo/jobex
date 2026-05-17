from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import JobSeekerProfileCampaignChannel
from apps.bots.bale.BaleProfile.models import BaleProfile
from apps.crm.customer.Jobseeker.jobs_application.serializers import CampaignChannelSerializer, JobSeekerProfileCampaignChannelSerializer , JobSeekerCampaignRequestListSerializer
from apps.crm.customer.Jobseeker.jobs_application.models import CampaignChannel
from apps.crm.customer.Jobseeker.jobs_application.permissions import IsAdminOrReadOnly


class CampaignViewSet(ModelViewSet):
    queryset = CampaignChannel.objects.all().order_by("-id")
    serializer_class = CampaignChannelSerializer
    permission_classes = [IsAdminOrReadOnly]



class JobSeekerCampaignChannelCreateView(CreateAPIView):
    queryset = JobSeekerProfileCampaignChannel.objects.all()
    serializer_class = JobSeekerProfileCampaignChannelSerializer
    


class JobSeekerCampaignRequestListView(ListAPIView):

    serializer_class = JobSeekerCampaignRequestListSerializer

    def get_queryset(self):

        chat_id = self.request.query_params.get("chat_id")

        try:
            bale_profile = BaleProfile.objects.select_related(
                "account__job_seeker_profile"
            ).get(chat_id=chat_id)
        except BaleProfile.DoesNotExist:
            raise ValidationError("کاربری با این شناسه یافت نشد.")

        profile = bale_profile.account.job_seeker_profile

        return JobSeekerProfileCampaignChannel.objects.filter(
            job_seeker_profile=profile
        ).select_related("campaign_channel").order_by("-created_at")
