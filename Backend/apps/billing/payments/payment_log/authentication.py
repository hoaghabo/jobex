from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from apps.bots.bale.BaleProfile.models import BaleProfile

class BotAuthentication(BaseAuthentication):
    def authenticate(self, request):
        bot_token = request.headers.get("X-Bot-Token")
        if not bot_token:
            return None  # این authentication رو skip کن، بقیه رو امتحان کن

        if bot_token != settings.BACKEND_BOT_API_TOKEN:
            raise AuthenticationFailed("Invalid bot token.")

        chat_id = request.data.get("chat_id") or request.query_params.get("chat_id")
        if not chat_id:
            raise AuthenticationFailed("chat_id is required.")

        try:
            profile = BaleProfile.objects.select_related("account").get(chat_id=chat_id)
        except BaleProfile.DoesNotExist:
            raise AuthenticationFailed("No user found with this chat_id.")

        return (profile.account, None)
