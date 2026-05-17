from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.bots.bale.BaleProfile.permissions import IsBaleUserByChatIdOrPhoneNumber

from apps.crm.customer.company.company_profile.models import CompanyProfile
from apps.crm.customer.company.job_posts.models import JobPosting
from apps.crm.customer.company.job_posts.serializer import (
    JobPostingSerializer,
    AdminJobPostingSerializer,
)
from apps.crm.models import CompanyMembership


def get_account_from_bale_user(request):
    """
    request.bale_user ممکن است یکی از این‌ها باشد:

    1. خود Account
    2. BaleProfile که فیلد account دارد

    این تابع همیشه Account برمی‌گرداند.
    """
    bale_user = getattr(request, "bale_user", None)

    if bale_user is None:
        raise ValidationError({
            "detail": "کاربر بله شناسایی نشد."
        })

    # اگر خود Account داخل request.bale_user قرار گرفته باشد
    if hasattr(bale_user, "phone_number") and not hasattr(bale_user, "account"):
        return bale_user

    # اگر BaleProfile داخل request.bale_user باشد
    account = getattr(bale_user, "account", None)

    if account is None:
        raise ValidationError({
            "detail": "اکانت مرتبط با کاربر بله پیدا نشد."
        })

    return account


def get_request_value(request, *keys):
    """
    مقدار را ابتدا از query_params و بعد از data می‌خواند.

    مثال:
    get_request_value(request, "company", "company_id")
    """
    for key in keys:
        value = request.query_params.get(key)
        if value not in [None, ""]:
            return value

    for key in keys:
        value = request.data.get(key)
        if value not in [None, ""]:
            return value

    return None


def parse_int_value(value, field_name):
    """
    مقدار عددی ورودی را validate و int می‌کند.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({
            field_name: f"{field_name} must be an integer."
        })


def get_company_membership_from_request(request):
    """
    عضویت شرکتی انتخاب‌شده کاربر را برمی‌گرداند.

    منطق:

    1. کاربر از request.bale_user استخراج می‌شود.
    2. membershipهای فعال کاربر گرفته می‌شود.
    3. اگر membership_id ارسال شده باشد:
       - چک می‌شود این membership متعلق به همین کاربر و فعال باشد.
    4. اگر company یا company_id ارسال شده باشد:
       - چک می‌شود کاربر عضو فعال آن شرکت باشد.
    5. اگر هیچ‌کدام ارسال نشده باشد:
       - اگر کاربر هیچ membership فعالی ندارد، خطا.
       - اگر فقط یک membership فعال دارد، همان انتخاب می‌شود.
       - اگر بیشتر از یک membership فعال دارد، خطا و درخواست company/membership_id.
    """
    account = get_account_from_bale_user(request)

    memberships = CompanyMembership.objects.select_related(
        "company",
        "role",
        "user",
    ).filter(
        user=account,
        is_active=True,
    )

    membership_id = get_request_value(request, "membership_id")
    company_id = get_request_value(request, "company", "company_id")

    if membership_id:
        membership_id = parse_int_value(membership_id, "membership_id")

        membership = memberships.filter(id=membership_id).first()

        if not membership:
            raise ValidationError({
                "membership_id": "This membership does not belong to the current user or is inactive."
            })

        return membership

    if company_id:
        company_id = parse_int_value(company_id, "company")

        membership = memberships.filter(company_id=company_id).first()

        if not membership:
            raise ValidationError({
                "company": "You are not an active member of this company."
            })

        return membership

    memberships_count = memberships.count()

    if memberships_count == 0:
        raise ValidationError({
            "detail": "No active company membership found for this user."
        })

    if memberships_count == 1:
        return memberships.first()

    raise ValidationError({
        "company": "You belong to multiple companies. Please provide company id or membership_id."
    })


def get_company_profile_from_request(request):
    """
    پروفایل شرکت متناظر با عضویت انتخاب‌شده کاربر را برمی‌گرداند.
    """
    membership = get_company_membership_from_request(request)

    try:
        return membership.company_profile
    except CompanyProfile.DoesNotExist:
        raise ValidationError({
            "detail": "برای این عضویت هنوز پروفایل شرکت ایجاد نشده است."
        })


class AdminJobPostingListCreateAPIView(generics.ListCreateAPIView):
    queryset = JobPosting.objects.select_related(
        "company",
        "created_by_membership",
        "created_by_membership__user",
    ).all()
    serializer_class = AdminJobPostingSerializer
    permission_classes = [IsAdminUser]


class AdminJobPostingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobPosting.objects.select_related(
        "company",
        "created_by_membership",
        "created_by_membership__user",
    ).all()
    serializer_class = AdminJobPostingSerializer
    permission_classes = [IsAdminUser]


class MyCompanyJobPostingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []

    def get_queryset(self):
        membership = get_company_membership_from_request(self.request)

        return JobPosting.objects.select_related(
            "company",
            "created_by_membership",
            "created_by_membership__user",
        ).filter(
            company_id=membership.company_id
        ).order_by("-id")

    def perform_create(self, serializer):
        membership = get_company_membership_from_request(self.request)

        serializer.save(
            company=membership.company,
            created_by_membership=membership,
        )


class MyCompanyJobPostingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        membership = get_company_membership_from_request(self.request)

        return JobPosting.objects.select_related(
            "company",
            "created_by_membership",
            "created_by_membership__user",
        ).filter(
            company_id=membership.company_id
        )

    def perform_update(self, serializer):
        """
        جلوگیری از تغییر شرکت آگهی در PATCH.

        حتی اگر کاربر در body فیلد company بفرستد،
        شرکت آگهی همان شرکت انتخاب‌شده باقی می‌ماند.
        """
        membership = get_company_membership_from_request(self.request)

        serializer.save(
            company=membership.company,
        )


def serialize_choices(choices):
    return [
        {
            "value": value,
            "label": label,
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
