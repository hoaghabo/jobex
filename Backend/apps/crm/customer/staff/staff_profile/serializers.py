from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = Employee
        fields = [
            'id',
            'mobile',
            'password',
            'first_name',
            'last_name',
            'personnel_code',
            'position',
            'hire_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['mobile'] = instance.user.mobile
        data['first_name'] = instance.user.first_name
        data['last_name'] = instance.user.last_name
        return data

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        user = User.objects.create(
            mobile=mobile,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()

        employee = Employee.objects.create(
            user=user,
            **validated_data
        )
        return employee

    def update(self, instance, validated_data):
        user = instance.user

        mobile = validated_data.pop('mobile', None)
        password = validated_data.pop('password', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)

        if mobile is not None:
            user.mobile = mobile
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if password:
            user.set_password(password)

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class EmployeeLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField(write_only=True)
