from django.contrib import admin

from apps.bots.bale.BaleProfile.models import BaleProfile


@admin.register(BaleProfile)
class BaleProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_id", "user_id", "username", "phone_number", "registered_full_name","is_synced", "bale_bot_name")
    search_fields = ("username", "chat_id", "username", "phone_number")
