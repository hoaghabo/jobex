from django.urls import path
from .views import BotUserRegisterAPIView, BotUserStatusAPIView

urlpatterns = [
    path("user/entry/", BotUserRegisterAPIView.as_view(), name="bot-user-entry"),
    path("user/status/", BotUserStatusAPIView.as_view(), name="bot-user-status"),
]
