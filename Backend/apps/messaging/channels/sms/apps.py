from django.apps import AppConfig


class SmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messaging.channels.sms"
    label = "messaging_sms"
