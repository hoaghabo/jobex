from rest_framework import serializers
from .models import JobSeekerProfileCampaignChannel, CampaignChannel
from apps.accounts.models import Accounts
from apps.bots.bale.BaleProfile.models import BaleProfile


class CampaignChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignChannel
        fields = "__all__"






class JobSeekerProfileCampaignChannelSerializer(serializers.ModelSerializer):

    chat_id = serializers.CharField(write_only=True)

    class Meta:
        model = JobSeekerProfileCampaignChannel
        fields = ["chat_id", "campaign_channel"]

    def create(self, validated_data):
        chat_id = validated_data.pop("chat_id")

        try:
            bale_profile = BaleProfile.objects.select_related(
                "account__job_seeker_profile"
            ).get(chat_id=chat_id)
        except BaleProfile.DoesNotExist:
            raise serializers.ValidationError("کاربری با این شناسه یافت نشد.")

        profile = bale_profile.account.job_seeker_profile
        campaign_channel = validated_data["campaign_channel"]

        status = JobSeekerProfileCampaignChannel.Status.USER_REQUEST

        # جلوگیری از درخواست تکراری
        exists = JobSeekerProfileCampaignChannel.objects.filter(
            job_seeker_profile=profile,
            campaign_channel=campaign_channel,
            status=status
        ).exists()

        if exists:
            raise serializers.ValidationError(
                "شما قبلاً برای این کمپین درخواست ثبت کرده‌اید."
            )

        obj = JobSeekerProfileCampaignChannel.objects.create(
            job_seeker_profile=profile,
            campaign_channel=campaign_channel,
            status=status
        )

        return obj



class JobSeekerCampaignRequestListSerializer(serializers.ModelSerializer):

    campaign_channel = CampaignChannelSerializer(read_only=True)

    class Meta:
        model = JobSeekerProfileCampaignChannel
        fields = [
            "id",
            "campaign_channel",
            "status",
            "created_at"
        ]
