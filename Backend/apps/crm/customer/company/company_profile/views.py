from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError

from apps.bots.bale.BaleProfile.permissions import IsBaleUserByChatIdOrPhoneNumber

from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.company_profile.serializer import CompanyProfileSerializer


class AdminCompanyProfileListAPIView(generics.ListCreateAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAdminUser]


class AdminCompanyProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAdminUser]


def get_account_from_bale_user(request):
    """
    request.bale_user ممکن است یکی از این‌ها باشد:
    1. Account
    2. BaleProfile که خودش account دارد

    این تابع همیشه باید Account برگرداند.
    """
    bale_user = getattr(request, "bale_user", None)

    if bale_user is None:
        raise ValidationError({
            "detail": "کاربر بله شناسایی نشد."
        })

    # اگر permission خود Account را داخل request.bale_user گذاشته باشد
    if hasattr(bale_user, "phone_number") and not hasattr(bale_user, "account"):
        return bale_user

    # اگر permission خود BaleProfile را داخل request.bale_user گذاشته باشد
    account = getattr(bale_user, "account", None)

    if account is None:
        raise ValidationError({
            "detail": "اکانت مرتبط با کاربر بله پیدا نشد."
        })

    return account


class MyCompanyProfileDetailsAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []
    http_method_names = ["get", "patch"]

    def get_object(self):
        account = get_account_from_bale_user(self.request)

        profile, created = CompanyProfile.objects.get_or_create(
            account=account
        )

        return profile


class CompanyProfileRegisterAPIView(generics.CreateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def perform_create(self, serializer):
        account = get_account_from_bale_user(self.request)

        if CompanyProfile.objects.filter(account=account).exists():
            raise ValidationError({
                "detail": "پروفایل شرکت برای این کاربر قبلاً ایجاد شده است."
            })

        serializer.save(account=account)
