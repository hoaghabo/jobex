from django.apps import AppConfig

class BotsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.bots'

    def ready(self):
        # Ensure the signals are imported when the app is ready
        import apps.bots.bale.BaleProfile.signals