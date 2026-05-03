from django.contrib import admin
from .models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        "bale_user_id",
        "chat_id",
        "display_name",
        "username",
        "phone_number",
        "age",
        "city",
        "is_registered",
        "is_active",
        "is_admin",
        "is_blocked",
        "last_state",
        "last_seen_at",
        "registered_at",
        "created_at",
    ]

    list_filter = [
        "is_registered",
        "is_active",
        "is_admin",
        "is_blocked",
        "city",
        "registered_at",
        "last_seen_at",
        "created_at",
    ]

    search_fields = [
        "bale_user_id",
        "chat_id",
        "first_name",
        "last_name",
        "username",
        "phone_number",
        "registered_full_name",
        "city",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "registered_at",
        "last_seen_at",
    ]

    fieldsets = [
        (
            "اطلاعات کاربر در بله",
            {
                "fields": [
                    "bale_user_id",
                    "chat_id",
                    "first_name",
                    "last_name",
                    "username",
                ]
            },
        ),
        (
            "اطلاعات ثبت‌نام",
            {
                "fields": [
                    "registered_full_name",
                    "phone_number",
                    "age",
                    "city",
                    "is_registered",
                    "registered_at",
                ]
            },
        ),
        (
            "وضعیت کاربر",
            {
                "fields": [
                    "is_active",
                    "is_admin",
                    "is_blocked",
                    "last_state",
                    "state_data",
                    "last_seen_at",
                ]
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ]
            },
        ),
    ]

    ordering = [
        "-created_at",
    ]

    list_per_page = 50

    @admin.display(description="نام")
    def display_name(self, obj):
        return (
            obj.registered_full_name
            or obj.first_name
            or obj.username
            or str(obj.bale_user_id)
        )
