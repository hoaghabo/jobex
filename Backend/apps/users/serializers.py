# apps/users/serializers.py

from django.contrib.auth import authenticate
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "access_level"]

class LoginSerializer(serializers.Serializer):
    # تغییر از email به username
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # استفاده از متد استاندارد جنگو برای احراز هویت با یوزرنیم
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("نام کاربری یا رمز عبور اشتباه است.")

        if not user.is_active:
            raise serializers.ValidationError("حساب کاربری غیرفعال است.")

        attrs["user"] = user
        return attrs
