from django.db import models
from apps.accounts.models import Accounts
from django.conf import settings



class BaleProfile(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bale_profiles"
    )


    chat_id = models.BigIntegerField(unique=True, null=False, blank=False)
    user_id = models.BigIntegerField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    profile_first_name = models.CharField(max_length=100, blank=True)
    profile_last_name = models.CharField(max_length=100, blank=True)
    registered_full_name = models.CharField(max_length=200, blank=False, null=False)
    bale_bot_name = models.CharField(max_length=200, null=True, blank=True)
    is_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    
    