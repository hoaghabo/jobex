from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView , ChoicesListAPIView , CityListAPIView , RegisterOrUpdateUserAPIView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("registered/", RegisterOrUpdateUserAPIView.as_view(), name="registered"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("choices/", ChoicesListAPIView.as_view(), name="choice_list"),
    path("city/", CityListAPIView.as_view(), name="city_list"),
]
