from rest_framework import serializers
from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'
        read_only_fields = ["account"]
        extra_kwargs = {
            "work_enthusiasts": {"required": False},
            "campaign_request": {"required": False},
        }
        
    def validate(self, data):
        # اگر work_enthusiasts یا campaign_request خالی بودند، مقدار پیش‌فرض [] را می‌دهیم
        if 'work_enthusiasts' not in data:
            data['work_enthusiasts'] = []
        if 'campaign_request' not in data:
            data['campaign_request'] = []
        return data
    
    
    
