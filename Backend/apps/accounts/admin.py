from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import Accounts, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("id",)


@admin.register(Accounts)
class AccountsAdmin(UserAdmin):
    model = Accounts

    list_display = (
        "id",
        "phone_number",
        "password",
        "first_name",
        "last_name",
        "email",
        "city",
        "gender",
        "is_bot_bale_member",
        "is_jobseeker_member",
        "is_company_member",
        "is_staff",
        "is_active",
    )

    ordering = ("id",)

    search_fields = (
        "phone_number",
        "email",
        "first_name",
        "last_name",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_bot_bale_member",
        "is_jobseeker_member",
        "is_company_member",
        "gender",
        "city",
    )

    fieldsets = (
        ("اطلاعات حساب", {
            "fields": (
                "phone_number",
                "password",
            )
        }),
        ("اطلاعات شخصی", {
            "fields": (
                "first_name",
                "last_name",
                "display_name",
                "email",
                "contact_number",
                "gender",
                "city",
                "day_birthdate",
                "month_birthdate",
                "year_birthdate",
            )
        }),
        ("وضعیت عضویت", {
            "fields": (
                "is_phone_verified",
                "is_registration_completed",
                "is_bot_bale_member",
                "is_jobseeker_member",
                "is_company_member",
            )
        }),
        ("دسترسی‌ها", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("تاریخ‌ها", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )
