import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.accounts.models import Accounts
from apps.bots.bale.BaleProfile.models import BaleProfile
from apps.bots.bale.BaleProfile.services import sync_bale_basic_info_to_accounts


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=BaleProfile, dispatch_uid="ensure_bale_profile_account_before_save")
def ensure_account_before_save(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return

    if instance.account_id:
        return

    if not instance.phone_number:
        raise ValueError("phone_number is required for BaleProfile")

    account, created = Accounts.objects.get_or_create(
        phone_number=instance.phone_number,
        defaults={
            "first_name": instance.profile_first_name or "",
            "last_name": instance.profile_last_name or "",
        },
    )

    instance.account = account


@receiver(post_save, sender=BaleProfile, dispatch_uid="sync_bale_profile_after_save")
def sync_bale_profile_after_save(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    if not instance.account_id:
        return

    logger.debug(f"Syncing BaleProfile for phone_number={instance.phone_number}")

    if not instance.is_synced:
        sync_bale_basic_info_to_accounts(bale_profile=instance)

        BaleProfile.objects.filter(pk=instance.pk).update(is_synced=True)

    Accounts.objects.filter(pk=instance.account_id).update(
        is_bot_bale_member=True
    )

    logger.debug(f"Account {instance.account_id} marked as is_bot_bale_member=True")
