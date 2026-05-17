from rest_framework import serializers
from .models import Accounts,City

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)



class ChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ChoicesListSerializer(serializers.Serializer):
    gender_choices = serializers.SerializerMethodField()

    def get_gender_choices(self, obj):
        return [
            {
                "value": choice.value,
                "label": choice.label,
            }
            for choice in Accounts.GenderChoices
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]
        
        

class AccountRegisterSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Accounts
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "gender",
            "city",
            "day_birthdate",
            "month_birthdate",
            "year_birthdate",
        ]

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("شماره موبایل الزامی است.")
        return value

    def create(self, validated_data):
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        user = Accounts.objects.create(
            first_name=first_name,
            last_name=last_name,
            display_name=f"{first_name} {last_name}".strip(),
            phone_number=validated_data["phone_number"],
            email=validated_data.get("email"),
            gender=validated_data.get("gender"),
            city=validated_data.get("city"),
            day_birthdate=validated_data.get("day_birthdate"),
            month_birthdate=validated_data.get("month_birthdate"),
            year_birthdate=validated_data.get("year_birthdate"),
            is_registration_completed=True,
        )
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.display_name = f"{instance.first_name} {instance.last_name}".strip()
        instance.email = validated_data.get("email", instance.email)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.city = validated_data.get("city", instance.city)
        instance.day_birthdate = validated_data.get("day_birthdate", instance.day_birthdate)
        instance.month_birthdate = validated_data.get("month_birthdate", instance.month_birthdate)
        instance.year_birthdate = validated_data.get("year_birthdate", instance.year_birthdate)
        instance.is_registration_completed = True
        instance.save()
        return instance