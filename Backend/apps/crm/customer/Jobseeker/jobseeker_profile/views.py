from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from apps.crm.customer.Jobseeker.jobseeker_profile.models import JobSeekerProfile
from apps.crm.customer.Jobseeker.jobseeker_profile.serializers import JobSeekerProfileSerializer
from apps.bots.bale.BaleProfile.permissions import IsBaleUserByChatIdOrPhoneNumber


def get_account_from_bale_user(request):
    """
    request.bale_user ممکن است یکی از این‌ها باشد:
    1. Account
    2. BaleProfile که خودش account دارد

    این تابع همیشه Account برمی‌گرداند.
    """
    bale_user = getattr(request, "bale_user", None)

    if bale_user is None:
        raise ValidationError({
            "detail": "کاربر بله شناسایی نشد."
        })

    # اگر خود Account باشد
    if hasattr(bale_user, "phone_number") and not hasattr(bale_user, "account"):
        return bale_user

    # اگر BaleProfile باشد
    account = getattr(bale_user, "account", None)
    if account is None:
        raise ValidationError({
            "detail": "اکانت مرتبط با کاربر بله پیدا نشد."
        })

    return account


class AdminJobseekerProfileListAPIView(generics.ListCreateAPIView):
    queryset = JobSeekerProfile.objects.all()
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAdminUser]


class AdminJobseekerProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobSeekerProfile.objects.all()
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAdminUser]


class MyJobseekerDetailsAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []
    http_method_names = ["get", "patch"]

    def get_object(self):
        account = get_account_from_bale_user(self.request)

        profile, created = JobSeekerProfile.objects.get_or_create(
            account=account
        )
        return profile


class JobseekerRegisterAPIView(generics.CreateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def perform_create(self, serializer):
        account = get_account_from_bale_user(self.request)

        if JobSeekerProfile.objects.filter(account=account).exists():
            raise ValidationError({
                "detail": "پروفایل جویای کار برای این کاربر قبلاً ایجاد شده است."
            })

        serializer.save(account=account)
        
        
        

def serialize_choices(choices):
    return [{"value": value, "label": label} for value, label in choices]


class JobSeekerChoicesAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        data = {
            "degree": serialize_choices(JobSeekerProfile.DegreeChoices.choices),
            "city": serialize_choices(JobSeekerProfile.CityChoices.choices),
            "work_enthusiasts": serialize_choices(JobSeekerProfile.WorkEnthusiastGroupChoices.choices),
            "salary_range": serialize_choices(JobSeekerProfile.SalaryRangeChoices.choices),
            "work_location_priority": serialize_choices(JobSeekerProfile.WorkLocationPriorityChoices.choices),
            "campaign_request": serialize_choices(JobSeekerProfile.CampaignRequestChoices.choices),
        }
        return Response(data)