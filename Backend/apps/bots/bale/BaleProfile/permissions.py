from rest_framework.permissions import BasePermission
from apps.accounts.models import Accounts

from apps.bots.bale.BaleProfile.models import BaleProfile


class IsBaleUserByPhoneNumber(BasePermission):
    message = "کاربر با این شماره موبایل یافت نشد یا عضو ربات بله نیست."

    def normalize_phone_number(self, phone_number):
        if not phone_number:
            return None

        phone_number = str(phone_number).strip().replace(" ", "").replace("-", "")

        if phone_number.startswith("+98"):
            phone_number = "0" + phone_number[3:]
        elif phone_number.startswith("98"):
            phone_number = "0" + phone_number[2:]

        return phone_number

    def has_permission(self, request, view):
        phone_number = (
            request.data.get("phone_number")
            or request.query_params.get("phone_number")
        )

        phone_number = self.normalize_phone_number(phone_number)
        print("PHONE_NUMBER:", phone_number)

        if not phone_number:
            self.message = "شماره موبایل ارسال نشده است."
            return False

        user = Accounts.objects.filter(phone_number=phone_number).first()

        if not user:
            self.message = "کاربر با این شماره موبایل یافت نشد."
            return False

        if not getattr(Accounts, "is_bot_bale_member", False):
            self.message = "این کاربر عضو ربات بله نیست."
            return False

        request.bale_user = user
        return True






class IsBaleUserByChatIdOrPhoneNumber(BasePermission):
    message = "کاربر با شماره موبایل یا chat_id پیدا نشد."

    def has_permission(self, request, view):
        phone_number = request.data.get("phone_number") or request.query_params.get("phone_number")
        chat_id = request.data.get("chat_id") or request.query_params.get("chat_id")

        print(f"====================> phone_number: {phone_number}")
        print(f"====================> chat_id: {chat_id}")

        bale_profile = None

        if phone_number:
            bale_profile = BaleProfile.objects.filter(phone_number=phone_number).first()

        if not bale_profile and chat_id:
            bale_profile = BaleProfile.objects.filter(chat_id=chat_id).first()

        if not bale_profile:
            return False

        request.bale_user = bale_profile
        return True