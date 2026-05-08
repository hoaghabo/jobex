from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.bots.bale.BaleProfile.permissions import IsBaleUserByChatIdOrPhoneNumber

from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.job_posts.models import JobPosting
from apps.crm.customer.company.job_posts.serializer import JobPostingSerializer
from apps.crm.customer.company.job_posts.serializer import (
    JobPostingSerializer,
    AdminJobPostingSerializer,
)



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



def get_company_profile_from_request(request):
    account = get_account_from_bale_user(request)

    try:
        return account.company_profile
    except CompanyProfile.DoesNotExist:
        raise ValidationError({
            "detail": "برای این کاربر هنوز پروفایل شرکت ایجاد نشده است."
        })


class AdminJobPostingListCreateAPIView(generics.ListCreateAPIView):
    queryset = JobPosting.objects.select_related("company", "company__account").all()
    serializer_class = AdminJobPostingSerializer
    permission_classes = [IsAdminUser]


class AdminJobPostingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobPosting.objects.select_related("company", "company__account").all()
    serializer_class = AdminJobPostingSerializer
    permission_classes = [IsAdminUser]


class MyCompanyJobPostingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def get_queryset(self):
        company_profile = get_company_profile_from_request(self.request)

        return JobPosting.objects.select_related(
            "company",
            "company__account"
        ).filter(
            company=company_profile
        )

    def perform_create(self, serializer):
        company_profile = get_company_profile_from_request(self.request)

        serializer.save(company=company_profile)



class MyCompanyJobPostingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        company_profile = get_company_profile_from_request(self.request)

        return JobPosting.objects.select_related(
            "company",
            "company__account"
        ).filter(
            company=company_profile
        )


def serialize_choices(choices):
    return [
        {
            "value": value,
            "label": label
        }
        for value, label in choices
    ]


class JobPostingChoicesAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        data = {
            "degree": serialize_choices(JobPosting.DegreeChoices.choices),
            "job_title": serialize_choices(JobPosting.JobTitleChoices.choices),
            "cooperation_type": serialize_choices(JobPosting.CooperationTypeChoices.choices),
            "attendance_type": serialize_choices(JobPosting.AttendanceTypeChoices.choices),
            "minimum_work_experience": serialize_choices(JobPosting.WorkExperienceChoices.choices),
            "working_days": serialize_choices(JobPosting.WorkingDaysChoices.choices),
            "working_hours": serialize_choices(JobPosting.WorkingHoursChoices.choices),
        }

        return Response(data)
