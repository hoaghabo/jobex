from rest_framework import serializers

from apps.crm.customer.company.job_posts.models import JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True
    )

    created_by_membership_id = serializers.IntegerField(
        source="created_by_membership.id",
        read_only=True
    )

    job_title_display = serializers.CharField(
        source="get_job_title_display",
        read_only=True
    )

    cooperation_type_display = serializers.CharField(
        source="get_cooperation_type_display",
        read_only=True
    )

    degree_display = serializers.CharField(
        source="get_degree_display",
        read_only=True
    )

    minimum_work_experience_display = serializers.CharField(
        source="get_minimum_work_experience_display",
        read_only=True
    )

    attendance_type_display = serializers.CharField(
        source="get_attendance_type_display",
        read_only=True
    )

    working_days_display = serializers.CharField(
        source="get_working_days_display",
        read_only=True
    )

    working_hours_display = serializers.CharField(
        source="get_working_hours_display",
        read_only=True
    )

    class Meta:
        model = JobPosting
        fields = "__all__"

        read_only_fields = [
            "company",
            "company_name",
            "created_by_membership",
            "created_by_membership_id",
            "created_at",
            "updated_at",

            "job_title_display",
            "cooperation_type_display",
            "degree_display",
            "minimum_work_experience_display",
            "attendance_type_display",
            "working_days_display",
            "working_hours_display",
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
    created_by_membership_id = serializers.IntegerField(
        source="created_by_membership.id",
        read_only=True
    )

    class Meta:
        model = JobPosting
        fields = "__all__"

        read_only_fields = [
            "company_name",
            "created_by_membership_id",
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
