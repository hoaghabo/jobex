from rest_framework import serializers
from .models import BaleProfile


class BaleProfileSerializers(serializers.ModelSerializer):
    is_bot_bale_member = serializers.BooleanField(
        source="account.is_bot_bale_member",
        read_only=True
    )
    is_jobseeker_member = serializers.BooleanField(
        source="account.is_jobseeker_member",
        read_only=True
    )
    is_company_member = serializers.BooleanField(
        source="account.is_company_member",
        read_only=True
    )

    class Meta:
        model = BaleProfile
        fields = "__all__"

    
    
class BaleRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaleProfile
        fields = [
            "id",
            "chat_id",
            "user_id",
            "bale_bot_name",
            "username",
            "registered_full_name",
            "phone_number",
        ]
        
        read_only = [
            "id"
        ]
    
    