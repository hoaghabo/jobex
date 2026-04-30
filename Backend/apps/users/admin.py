from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "access_level",
        "is_staff",
        "is_active",
    ]

    list_filter = [
        "access_level",
        "is_staff",
        "is_active",
    ]

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Access Control",
            {
                "fields": (
                    "access_level",
                    "phone_number",
                )
            },
        ),
    )

    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Access Control",
            {
                "fields": (
                    "access_level",
                    "phone_number",
                )
            },
        ),
    )
