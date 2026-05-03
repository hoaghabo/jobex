from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import BotUser


class BotUserRegisterAPIView(APIView):
    """
    API حرفه‌ای ثبت / آپدیت کاربر + مدیریت وضعیت
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # =========================
        # 1. Auth
        # =========================
        bot_token = request.headers.get("X-Bot-Token")
        expected_token = getattr(settings, "BOT_API_TOKEN", None)

        if expected_token and bot_token != expected_token:
            return Response(
                {"ok": False, "code": "INVALID_TOKEN"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = request.data
        bale_user_id = data.get("bale_user_id")

        if not bale_user_id:
            return Response(
                {"ok": False, "code": "BALE_USER_ID_REQUIRED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =========================
        # 2. Get existing user (برای کنترل بهتر)
        # =========================
        try:
            user = BotUser.objects.get(bale_user_id=bale_user_id)
            created = False
        except BotUser.DoesNotExist:
            user = None
            created = True

        # =========================
        # 3. اگر کاربر بلاک شده → خروج
        # =========================
        if user and user.is_blocked:
            return Response(
                {"ok": False, "code": "USER_BLOCKED"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # =========================
        # 4. ساخت defaults هوشمند
        # =========================
        defaults = {
            "chat_id": data.get("chat_id"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "username": data.get("username"),
            "last_seen_at": timezone.now(),
            "is_active": True,
        }

        # حذف None
        defaults = {k: v for k, v in defaults.items() if v is not None}

        # =========================
        # 5. ایجاد یا آپدیت کاربر
        # =========================
        user, created = BotUser.objects.update_or_create(
            bale_user_id=bale_user_id,
            defaults=defaults,
        )

        # =========================
        # 6. مدیریت STATE (خیلی مهم برای ربات)
        # =========================
        state = data.get("state")
        state_data = data.get("state_data")

        if state is not None:
            user.last_state = state

        if state_data is not None:
            user.state_data = state_data

        # =========================
        # 7. ثبت‌نام مرحله‌ای (نه overwrite کورکورانه)
        # =========================
        full_name = data.get("registered_full_name")
        phone = data.get("phone_number")
        age = data.get("age")
        city = data.get("city")

        if not user.is_registered:
            if full_name:
                user.registered_full_name = full_name

            if phone:
                user.phone_number = phone

            if age:
                # اعتبارسنجی ساده
                try:
                    age = int(age)
                    if 10 <= age <= 100:
                        user.age = age
                except:
                    pass

            if city:
                user.city = city

            # اگر همه فیلدها کامل شد → ثبت‌نام نهایی
            if (
                user.registered_full_name
                and user.phone_number
            ):
                user.is_registered = True
                user.registered_at = timezone.now()
                user.last_state = None
                user.state_data = {}

        # =========================
        # 8. ذخیره تغییرات
        # =========================
        user.save()

        # =========================
        # 9. پاسخ حرفه‌ای برای ربات
        # =========================
        return Response(
            {
                "ok": True,
                "created": created,
                "user": {
                    "id": user.id,
                    "bale_user_id": user.bale_user_id,
                    "chat_id": user.chat_id,

                    "is_registered": user.is_registered,
                    "is_blocked": user.is_blocked,
                    "is_active": user.is_active,

                    "state": user.last_state,
                },
                "meta": {
                    "needs_registration": not user.is_registered,
                },
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        

class BotUserStatusAPIView(APIView):
    """
    بررسی وضعیت کاربر برای ربات:
    - بلاک بودن
    - ثبت‌نام بودن
    - state فعلی
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        bot_token = request.headers.get("X-Bot-Token")
        expected_token = getattr(settings, "BOT_API_TOKEN", None)

        if expected_token and bot_token != expected_token:
            return Response(
                {"ok": False, "code": "INVALID_TOKEN"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        bale_user_id = request.data.get("bale_user_id")
        chat_id = request.data.get("chat_id")

        if not bale_user_id:
            return Response(
                {"ok": False, "code": "BALE_USER_ID_REQUIRED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = BotUser.objects.get_or_create(
            bale_user_id=bale_user_id,
            defaults={
                "chat_id": chat_id,
                "first_name": request.data.get("first_name"),
                "last_name": request.data.get("last_name"),
                "username": request.data.get("username"),
                "last_seen_at": timezone.now(),
                "is_active": True,
            },
        )

        updated = False

        if chat_id is not None and user.chat_id != chat_id:
            user.chat_id = chat_id
            updated = True

        first_name = request.data.get("first_name")
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True

        last_name = request.data.get("last_name")
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True

        username = request.data.get("username")
        if username and user.username != username:
            user.username = username
            updated = True

        user.last_seen_at = timezone.now()
        updated = True

        if updated:
            user.save()

        return Response(
            {
                "ok": True,
                "created": created,
                "user": {
                    "id": user.id,
                    "bale_user_id": user.bale_user_id,
                    "chat_id": user.chat_id,
                    "is_blocked": user.is_blocked,
                    "is_registered": user.is_registered,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "state": user.last_state,
                    "state_data": user.state_data,
                    "phone_number": user.phone_number,
                },
            },
            status=status.HTTP_200_OK,
        )