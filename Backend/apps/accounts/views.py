
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import LoginSerializer
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
