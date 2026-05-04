from django.contrib import admin
from apps.accounts.models import Accounts

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "phone_number", 
        "username", 
        "email", 
        "is_bot_bale_member",  # Corrected field name
        "is_jobseeker_member", 
        "is_company_member"
    )