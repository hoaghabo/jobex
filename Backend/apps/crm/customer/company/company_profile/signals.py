from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Accounts
from apps.crm.customer.company.company_profile.models import CompanyProfile


@receiver(post_save, sender=CompanyProfile, dispatch_uid="set_company_member_on_account")
def set_company_member(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    if not instance.account_id:
        return

    if created:
        Accounts.objects.filter(pk=instance.account_id).update(
            is_company_member=True
        )




