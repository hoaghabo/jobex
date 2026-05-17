from django.db import models
from apps.crm.customer.company.company_profile.models import CompanyProfile as Company
from apps.accounts.models import Accounts



class CompanyRole(models.Model):

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CompanyMembership(models.Model):

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

    role = models.ForeignKey(
        CompanyRole,
        on_delete=models.PROTECT
    )

    is_active = models.BooleanField(default=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"],
                name="unique_user_company_membership"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.company}"
