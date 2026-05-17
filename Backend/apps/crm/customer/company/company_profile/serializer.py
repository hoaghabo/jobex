from rest_framework import serializers
from django.db import transaction
from apps.bots.bale.BaleProfile.models import BaleProfile
from apps.crm.customer.company.company_membership.models import CompanyMembership, CompanyRole
from .models import CompanyProfile


class CompanyProfileSerializer(serializers.ModelSerializer):

    chat_id = serializers.CharField(write_only=True, required=False)

    role = serializers.PrimaryKeyRelatedField(
        queryset=CompanyRole.objects.all(),
        write_only=True,
        required=False
    )

    # ✅ فیلدهای خروجی خواندنی
    organization_size_label = serializers.CharField(
        source="get_organization_size_display",
        read_only=True
    )

    city_name = serializers.CharField(
        source="city.name",
        read_only=True
    )

    role_code = serializers.CharField(
        source="company_membership.role.code",
        read_only=True
    )

    role_name = serializers.CharField(
        source="company_membership.role.name",
        read_only=True
    )

    class Meta:
        model = CompanyProfile
        fields = "__all__"  # این را نگه می‌داریم
        read_only_fields = ["company_membership", "is_registration_complete"]

    def validate(self, attrs):
        request = self.context.get("request")

        chat_id = attrs.get("chat_id")
        role = attrs.get("role")

        # فقط هنگام create بررسی شود
        if request and request.method == "POST":

            if not chat_id:
                raise serializers.ValidationError(
                    {"chat_id": "chat_id الزامی است"}
                )

            if not role:
                raise serializers.ValidationError(
                    {"role": "role الزامی است"}
                )

            try:
                bale_profile = BaleProfile.objects.select_related("account").get(
                    chat_id=chat_id
                )
            except BaleProfile.DoesNotExist:
                raise serializers.ValidationError(
                    {"chat_id": "کاربری با این chat_id پیدا نشد"}
                )

            attrs["account"] = bale_profile.account

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        account = validated_data.pop("account")
        role = validated_data.pop("role")
        validated_data.pop("chat_id", None)

        company_name = validated_data.get("company_name")

        # جلوگیری از ثبت شرکت تکراری برای همان کاربر
        if CompanyProfile.objects.filter(
            company_name=company_name,
            memberships__user=account
        ).exists():
            raise serializers.ValidationError({
                "company_name": "این شرکت قبلاً توسط شما ثبت شده است."
            })

        company_profile = CompanyProfile.objects.create(**validated_data)

        membership = CompanyMembership.objects.create(
            user=account,
            company=company_profile,
            role=role
        )

        company_profile.company_membership = membership
        company_profile.save(update_fields=["company_membership"])

        company_profile.update_registration_status()

        return company_profile



    @transaction.atomic
    def update(self, instance, validated_data):

        role = validated_data.pop("role", None)
        validated_data.pop("chat_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if role:
            membership = instance.company_membership

            if membership:
                membership.role = role
                membership.save(update_fields=["role"])

        instance.update_registration_status()

        return instance


def serialize_choices(choices):
    return [
        {
            "id": value,
            "name": label
        }
        for value, label in choices
    ]