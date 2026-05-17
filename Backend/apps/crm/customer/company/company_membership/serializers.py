from rest_framework import serializers
from .models import CompanyMembership
from apps.bots.bale.BaleProfile.models import BaleProfile
from apps.accounts.models import Accounts
from .models import CompanyRole




class CompanyMembershipSerializer(serializers.ModelSerializer):

    chat_id = serializers.CharField(write_only=True)

    class Meta:
        model = CompanyMembership
        fields = [
            "id",
            "chat_id",
            "company",
            "role",
            "is_active",
            "joined_at",
        ]

        read_only_fields = ["joined_at"]

    def create(self, validated_data):

        chat_id = validated_data.pop("chat_id")

        try:
            bale_profile = BaleProfile.objects.select_related("account").get(
                chat_id=chat_id
            )
        except BaleProfile.DoesNotExist:
            raise serializers.ValidationError("کاربری با این chat_id پیدا نشد")

        validated_data["user"] = bale_profile.account

        return super().create(validated_data)





class CompanyRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyRole
        fields = ["id", "name", "code"]

    def validate_code(self, value):
        return value.lower()
