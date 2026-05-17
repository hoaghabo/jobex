from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.crm.customer.company.company_membership.models import CompanyMembership
from rest_framework.exceptions import NotFound
from apps.bots.bale.BaleProfile.models import BaleProfile
from apps.bots.bale.BaleProfile.permissions import IsBaleUserByChatIdOrPhoneNumber
from rest_framework.response import Response
from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.company_profile.serializer import CompanyProfileSerializer, serialize_choices
from .models import CompanyProfile


class AdminCompanyProfileListAPIView(generics.ListCreateAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        profile = serializer.save()
        profile.update_registration_status()


class AdminCompanyProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        profile = serializer.save()
        profile.update_registration_status()


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

class MyCompanyProfileDetailsAPIView(generics.ListAPIView):

    serializer_class = CompanyProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def get_queryset(self):

        account = get_account_from_bale_user(self.request)

        memberships = CompanyMembership.objects.filter(user=account)

        if not memberships.exists():
            raise NotFound("کاربر عضو هیچ شرکتی نیست")

        return CompanyProfile.objects.filter(
            memberships__user=account
        ).distinct()


class CompanyProfileRegisterAPIView(generics.CreateAPIView):

    serializer_class = CompanyProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def perform_create(self, serializer):

        profile = serializer.save()

        profile.update_registration_status()




class CompanyChoicesAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        data = {
            "organization_size": serialize_choices(
                CompanyProfile.OrganizationSizeChoices.choices
            ),
        }

        return Response(data)
    
    
    
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny  # اگر auth نداری


class MyCompanyProfileDetailAPIView(RetrieveUpdateAPIView):

    serializer_class = CompanyProfileSerializer
    permission_classes = [AllowAny]  # اگر auth سفارشی نداری

    def get_object(self):

        chat_id = self.request.query_params.get("chat_id")

        bale_profile = BaleProfile.objects.select_related("account").filter(
            chat_id=chat_id
        ).first()

        if not bale_profile:
            raise NotFound("کاربر پیدا نشد")

        account = bale_profile.account

        company = CompanyProfile.objects.filter(
            pk=self.kwargs["pk"],
            memberships__user=account
        ).first()

        if not company:
            raise NotFound("این شرکت متعلق به شما نیست")

        return company
