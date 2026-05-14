from django.db import models
from apps.crm.customer.company.company_profile.models import CompanyProfile as Company
from apps.accounts.models import Accounts

class CompanyMembership(models.Model):
    class RoleChoices(models.TextChoices):
        OWNER = "owner", "مالک"
        ADMIN = "admin", "ادمین"
        HR = "hr", "منابع انسانی"
        RECRUITER = "recruiter", "استخدام"
        MEMBER = "member", "عضو"

    user = models.ForeignKey(
        Accounts,
        on_delete=models.CASCADE,
        related_name="company_memberships"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user.phone_number} - {self.company.name} - {self.role}"
