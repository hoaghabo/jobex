from rest_framework import serializers
from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    degree_display = serializers.CharField(
        source="get_degree_display",
        read_only=True
    )
    salary_range_display = serializers.CharField(
        source="get_salary_range_display",
        read_only=True
    )
    work_location_priority_display = serializers.CharField(
        source="get_work_location_priority_display",
        read_only=True
    )
    work_enthusiasts_display = serializers.SerializerMethodField()

    class Meta:
        model = JobSeekerProfile
        fields = [
            "id",
            "account",
            "degree",
            "degree_display",
            "work_enthusiasts",
            "work_enthusiasts_display",
            "salary_range",
            "salary_range_display",
            "work_location_priority",
            "work_location_priority_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["account"]
        extra_kwargs = {
            "work_enthusiasts": {"required": False},
            "resume_file_id": {"required": False, "allow_null": True, "allow_blank": True},

        }

    def validate(self, data):
        if "work_enthusiasts" not in data:
            data["work_enthusiasts"] = []
        return data

    def get_work_enthusiasts_display(self, obj):
        if not obj.work_enthusiasts:
            return []

        choices_map = dict(JobSeekerProfile.WorkEnthusiastGroupChoices.choices)

        return [
            choices_map.get(value, value)
            for value in obj.work_enthusiasts
        ]
