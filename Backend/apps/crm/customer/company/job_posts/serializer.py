from rest_framework import serializers

from apps.crm.customer.company.job_posts.models import JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True
    )

    class Meta:
        model = JobPosting
        fields = "__all__"

        read_only_fields = [
            "company",
            "company_name",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "degree": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "working_hours_description": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "salary_description": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "benefits": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "has_overtime": {
                "required": False,
            },
            "is_salary_negotiable": {
                "required": False,
            },
        }


class AdminJobPostingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True
    )

    class Meta:
        model = JobPosting
        fields = "__all__"

        read_only_fields = [
            "company_name",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "degree": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "working_hours_description": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "salary_description": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "benefits": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "has_overtime": {
                "required": False,
            },
            "is_salary_negotiable": {
                "required": False,
            },
        }
