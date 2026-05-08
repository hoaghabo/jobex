from rest_framework import serializers
from apps.crm.customer.company.company_profile.models import CompanyProfile


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"
        read_only_fields = ["account", "created_at", "updated_at"]

        extra_kwargs = {
            "fullname": {
                "required": False,
                "allow_blank": True,
            },
            "company_name": {
                "required": False,
                "allow_blank": True,
            },
            "phone_number": {
                "required": False,
                "allow_blank": True,
            },
            "email": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "organization_size": {
                "required": False,
                "allow_null": True,
            },
            "city": {
                "required": False,
                "allow_null": True,
            },
            "industry": {
                "required": False,
                "allow_blank": True,
            },
            "full_address": {
                "required": False,
                "allow_blank": True,
            },
            "website": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "landline_phone": {
                "required": False,
                "allow_blank": True,
            },
        }
