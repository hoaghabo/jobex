from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import Accounts


@admin.register(Accounts)
class AccountsAdmin(UserAdmin):
    model = Accounts

    list_display = (
        "id",
        "phone_number",
        "email",
        "is_bot_bale_member",
        "is_jobseeker_member",
        "is_company_member",
        "is_staff",
        "is_active",
    )

    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("phone_number", "email", "password")}),
        ("Membership", {
            "fields": (
                "is_bot_bale_member",
                "is_jobseeker_member",
                "is_company_member",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "email",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    search_fields = ("phone_number", "email")
