
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import LoginSerializer , ChoicesListSerializer , CitySerializer , AccountRegisterSerializer
from .models import City , Accounts
from .utils import get_tokens_for_user



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is None:
            return Response(
                {"detail": "شماره موبایل یا رمز عبور اشتباه است."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"detail": "حساب کاربری غیرفعال است."},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "is_phone_verified": user.is_phone_verified,
                "is_registration_completed": user.is_registration_completed,
                "is_bot_bale_member": user.is_bot_bale_member,
                "is_jobseeker_member": user.is_jobseeker_member,
                "is_company_member": user.is_company_member,
            },
            "accessToken": tokens["access"],
            "refreshToken": tokens["refresh"],
        }, status=status.HTTP_200_OK)



class ChoicesListAPIView(APIView):
    def get(self, request):
        serializer = ChoicesListSerializer(instance={})
        return Response(serializer.data)
    
class CityListAPIView(APIView):
    def get(self, request):
        cities = City.objects.all().order_by("name")
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class RegisterOrUpdateUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response(
                {"detail": "phone_number الزامی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Accounts.objects.filter(phone_number=phone_number).first()

        if user:
            serializer = AccountRegisterSerializer(user, data=request.data, partial=True)
            action = "updated"
        else:
            serializer = AccountRegisterSerializer(data=request.data)
            action = "created"

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "status": "success",
                "action": action,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "display_name": user.display_name,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "gender": user.gender,
                    "city": user.city.slug if user.city else None,
                    "city_name": user.city.name if user.city else None,
                    "day_birthdate": user.day_birthdate,
                    "month_birthdate": user.month_birthdate,
                    "year_birthdate": user.year_birthdate,
                    "is_registration_completed": user.is_registration_completed,
                },
            },
            status=status.HTTP_200_OK,
        )