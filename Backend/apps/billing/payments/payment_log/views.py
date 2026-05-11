import requests

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.bot.bot_notify import notify_user_payment_success
from apps.billing.payments.payment_log.authentication import BotAuthentication
from apps.billing.orders.order_log.models import Order
from apps.billing.payments.payment_log.models import Payment
from apps.billing.payments.payment_log.serializers import (
    ApproveCardToCardPaymentSerializer,
    ConfirmBaleWalletPaymentSerializer,
    CreatePaymentResponseSerializer,
    CreatePaymentSerializer,
    PaymentSerializer,
    PaymentStatusSerializer,
    RejectCardToCardPaymentSerializer,
    SubmitCardToCardReceiptSerializer,
    ZarinpalCallbackSerializer,
)


def get_product_snapshot(product_id):
    """
    این تابع را باید با مدل واقعی محصول خودت هماهنگ کنی.
    فعلاً بر اساس product_profile نوشتم.
    """

    from apps.billing.products.product_profile.models import Product

    product = get_object_or_404(Product, id=product_id)

    amount = (
        getattr(product, "final_price", None)
        or getattr(product, "price", None)
        or getattr(product, "amount", None)
        or getattr(product, "base_price", None)
    )

    if amount is None:
        raise ValueError("فیلد قیمت محصول پیدا نشد. یکی از final_price یا price یا amount لازم است.")

    title = (
        getattr(product, "title", None)
        or getattr(product, "name", None)
        or str(product)
    )

    return {
        "id": str(product.id),
        "title": title,
        "amount": int(amount),
        "raw": {
            "str": str(product),
        },
    }


def get_zarinpal_request_url():
    if getattr(settings, "ZARINPAL_SANDBOX", True):
        return "https://sandbox.zarinpal.com/pg/v4/payment/request.json"

    return "https://api.zarinpal.com/pg/v4/payment/request.json"


def get_zarinpal_verify_url():
    if getattr(settings, "ZARINPAL_SANDBOX", True):
        return "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"

    return "https://api.zarinpal.com/pg/v4/payment/verify.json"


def get_zarinpal_startpay_url(authority):
    if getattr(settings, "ZARINPAL_SANDBOX", True):
        return f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"

    return f"https://www.zarinpal.com/pg/StartPay/{authority}"


class CreatePaymentView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gateway = serializer.validated_data["gateway"]
        product_id = serializer.validated_data["product_id"]
        description = serializer.validated_data.get("description", "")

        try:
            product_snapshot = get_product_snapshot(product_id)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = product_snapshot["amount"]

        if gateway == Payment.Gateway.ZARINPAL:
            payment = self.create_zarinpal_payment(
                request=request,
                product_id=product_id,
                product_snapshot=product_snapshot,
                amount=amount,
                description=description,
                serializer=serializer,
            )

        elif gateway == Payment.Gateway.CARD_TO_CARD:
            payment = self.create_card_to_card_payment(
                request=request,
                product_id=product_id,
                product_snapshot=product_snapshot,
                amount=amount,
                description=description,
            )

        elif gateway == Payment.Gateway.BALE_WALLET:
            payment = self.create_bale_wallet_payment(
                request=request,
                product_id=product_id,
                product_snapshot=product_snapshot,
                amount=amount,
                description=description,
                serializer=serializer,
            )

        else:
            return Response(
                {"detail": "درگاه پرداخت نامعتبر است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CreatePaymentResponseSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )

    def create_zarinpal_payment(
        self,
        request,
        product_id,
        product_snapshot,
        amount,
        description,
        serializer,
    ):
        callback_url = getattr(settings, "ZARINPAL_CALLBACK_URL", None)
        ZARINPAL_MERCHANT_ID = getattr(settings, "ZARINPAL_MERCHANT_ID", None)

        if not callback_url:
            callback_url = request.build_absolute_uri(
                "/api/billing/payments/zarinpal/callback/"
            )

        payload = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": callback_url,
            "description": description or f"خرید محصول {product_id}"
        }
        print(payload)

        payment = Payment.objects.create(
            user=request.user,
            gateway=Payment.Gateway.ZARINPAL,
            status=Payment.Status.PENDING,
            product_id=str(product_id),
            product_data=product_snapshot,
            amount=amount,
            currency=getattr(settings, "BILLING_DEFAULT_CURRENCY", "IRR"),
            description=description,
            request_payload=payload,
        )

        try:
            response = requests.post(
                get_zarinpal_request_url(),
                json=payload,
                timeout=20,
            )
            response_data = response.json()
            print(f"=====================>> {response_data}")
        except Exception as exc:
            payment.status = Payment.Status.FAILED
            payment.request_response = {
                "error": str(exc),
            }
            print(f"=====================>> {payment.request_response}")
            payment.save(update_fields=[
                "status",
                "request_response",
                "updated_at",
            ])
            return payment

        payment.request_response = response_data

        data = response_data.get("data") or {}
        errors = response_data.get("errors") or {}

        authority = data.get("authority")
        code = data.get("code")

        if code == 100 and authority:
            payment.authority = authority
            payment.payment_url = get_zarinpal_startpay_url(authority)
            payment.status = Payment.Status.PENDING
        else:
            payment.status = Payment.Status.FAILED
            payment.verify_response = {
                "errors": errors,
                "response": response_data,
            }

        payment.save(update_fields=[
            "authority",
            "payment_url",
            "status",
            "request_response",
            "verify_response",
            "updated_at",
        ])

        return payment

    def create_card_to_card_payment(
        self,
        request,
        product_id,
        product_snapshot,
        amount,
        description,
    ):
        payment = Payment.objects.create(
            user=request.user,
            gateway=Payment.Gateway.CARD_TO_CARD,
            status=Payment.Status.WAITING_FOR_RECEIPT,
            manual_review_status=Payment.ManualReviewStatus.NONE,
            product_id=str(product_id),
            product_data=product_snapshot,
            amount=amount,
            currency=getattr(settings, "BILLING_DEFAULT_CURRENCY", "IRR"),
            description=description,
            destination_card_number=getattr(settings, "BILLING_CARD_TO_CARD_NUMBER", ""),
            destination_card_owner=getattr(settings, "BILLING_CARD_TO_CARD_OWNER", ""),
        )

        return payment

    def create_bale_wallet_payment(
        self,
        request,
        product_id,
        product_snapshot,
        amount,
        description,
        serializer,
    ):
        """
        ایجاد پرداخت کیف پول بله با استفاده از sendInvoice
        """
        BALE_BOT_TOKEN = getattr(settings, "BALE_BOT_TOKEN", None)
        BALE_PROVIDER_TOKEN = getattr(settings, "BALE_PROVIDER_TOKEN", "")
        
        if not BALE_BOT_TOKEN:
            raise ValueError("توکن ربات بله تنظیم نشده است.")
        
        # دریافت chat_id از serializer
        chat_id = serializer.validated_data.get("chat_id")
        if not chat_id:
            raise ValueError("chat_id الزامی است.")
        
        # ایجاد payload یکتا برای تشخیص پرداخت
        invoice_payload = f"product_{product_id}_user_{request.user.id}_{int(timezone.now().timestamp())}"
        
        # ساخت prices به فرمت LabeledPrice
        prices = [
            {
                "label": product_snapshot["title"][:32],
                "amount": amount
            }
        ]
        
        # فراخوانی sendInvoice
        send_invoice_payload = {
            "chat_id": chat_id,
            "title": product_snapshot["title"][:32],
            "description": (description or f"خرید {product_snapshot['title']}")[:255],
            "payload": invoice_payload[:128],
            "provider_token": BALE_PROVIDER_TOKEN,
            "prices": prices
        }
        
        # ایجاد رکورد پرداخت
        payment = Payment.objects.create(
            user=request.user,
            gateway=Payment.Gateway.BALE_WALLET,
            status=Payment.Status.PENDING,
            product_id=str(product_id),
            product_data=product_snapshot,
            amount=amount,
            currency="IRR",
            description=description,
            request_payload=send_invoice_payload,
            wallet_payload={
                "invoice_payload": invoice_payload,
                "chat_id": chat_id,
            },
        )
        
        try:
            # ارسال درخواست به API بله
            response = requests.post(
                f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendInvoice",
                json=send_invoice_payload,
                timeout=20,
            )
            response_data = response.json()
            
            payment.request_response = response_data
            
            if response_data.get("ok"):
                # پیام ارسال‌شده را ذخیره می‌کنیم
                result = response_data.get("result", {})
                message_id = result.get("message_id")
                
                payment.authority = invoice_payload  # ذخیره payload برای تطبیق بعدی
                payment.wallet_payload = {
                    "invoice_payload": invoice_payload,
                    "chat_id": chat_id,
                    "message_id": message_id,
                }
                payment.status = Payment.Status.PENDING
            else:
                payment.status = Payment.Status.FAILED
                payment.verify_response = {
                    "error": response_data.get("description", "خطای ناشناخته"),
                    "response": response_data,
                }
            
            payment.save(update_fields=[
                "authority",
                "wallet_payload",
                "status",
                "request_response",
                "verify_response",
                "updated_at",
            ])
            
        except Exception as exc:
            payment.status = Payment.Status.FAILED
            payment.request_response = {"error": str(exc)}
            payment.save(update_fields=[
                "status",
                "request_response",
                "updated_at",
            ])
        
        return payment


class ZarinpalCallbackView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def get(self, request):
        serializer = ZarinpalCallbackSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        authority = serializer.validated_data["Authority"]
        callback_status = serializer.validated_data["Status"]

        payment = get_object_or_404(
            Payment,
            gateway=Payment.Gateway.ZARINPAL,
            authority=authority,
        )

        payment.callback_payload = dict(request.GET)

        context = {
            "success": False,
            "title": "نتیجه پرداخت",
            "message": "",
            "ref_id": None,
            "payment_id": payment.id,
            "bot_url": getattr(settings, "BOT_START_URL", "#"),
        }

        if callback_status != "OK":
            payment.status = Payment.Status.CANCELED
            payment.save(update_fields=[
                "callback_payload",
                "status",
                "updated_at",
            ])

            context.update({
                "title": "پرداخت لغو شد",
                "message": "فرآیند پرداخت توسط کاربر لغو شد.",
            })
            return render(request, "templates/payments/zarinpal_result.html", context)

        verify_payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": payment.amount,
            "authority": authority,
        }

        payment.verify_payload = verify_payload

        try:
            response = requests.post(
                get_zarinpal_verify_url(),
                json=verify_payload,
                timeout=20,
            )
            response_data = response.json()
        except Exception as exc:
            payment.status = Payment.Status.FAILED
            payment.verify_response = {"error": str(exc)}
            payment.save(update_fields=[
                "callback_payload",
                "verify_payload",
                "verify_response",
                "status",
                "updated_at",
            ])

            context.update({
                "title": "خطا در تایید پرداخت",
                "message": "در هنگام بررسی نهایی پرداخت خطایی رخ داد. لطفاً چند لحظه بعد دوباره وضعیت را بررسی کنید.",
            })
            return render(request, "templates/payments/zarinpal_result.html", context)

        payment.verify_response = response_data
        data = response_data.get("data") or {}
        code = data.get("code")

        if code in [100, 101]:
            payment.status = Payment.Status.PAID
            payment.ref_id = str(data.get("ref_id", ""))
            payment.card_pan = str(data.get("card_pan", ""))
            payment.fee_type = str(data.get("fee_type", ""))
            payment.fee = data.get("fee")
            payment.paid_at = payment.paid_at or timezone.now()

            payment.save(update_fields=[
                "callback_payload",
                "verify_payload",
                "verify_response",
                "status",
                "ref_id",
                "card_pan",
                "fee_type",
                "fee",
                "paid_at",
                "updated_at",
            ])

            Order.objects.get_or_create_from_payment(payment)

            # ارسال پیام موفقیت به کاربر
            try:
                notify_user_payment_success(payment)
            except Exception:
                pass

            context.update({
                "success": True,
                "title": "پرداخت با موفقیت انجام شد",
                "message": "پرداخت شما با موفقیت ثبت شد. اطلاعات خرید برای شما در ربات ارسال شد.",
                "ref_id": payment.ref_id,
            })
            return render(request, "templates/payments/zarinpal_result.html", context)

        payment.status = Payment.Status.FAILED
        payment.save(update_fields=[
            "callback_payload",
            "verify_payload",
            "verify_response",
            "status",
            "updated_at",
        ])

        context.update({
            "title": "پرداخت ناموفق بود",
            "message": "پرداخت شما تایید نشد. در صورت کسر وجه، مبلغ طبق قوانین بانکی بازمی‌گردد.",
        })
        return render(request, "payments/zarinpal_result.html", context)


class SubmitCardToCardReceiptView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitCardToCardReceiptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            id=serializer.validated_data["payment_id"],
            user=request.user,
            gateway=Payment.Gateway.CARD_TO_CARD,
        )

        extra_payload = {
            "source": serializer.validated_data.get("source", ""),
            "message_id": serializer.validated_data.get("message_id", ""),
            "chat_id": serializer.validated_data.get("chat_id", ""),
        }

        try:
            payment.submit_card_to_card_receipt(
                receipt_image=serializer.validated_data.get("receipt_image"),
                receipt_file_id=serializer.validated_data.get("receipt_file_id", ""),
                receipt_tracking_code=serializer.validated_data.get("receipt_tracking_code", ""),
                extra_payload=extra_payload,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PaymentStatusSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class ApproveCardToCardPaymentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ApproveCardToCardPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            id=serializer.validated_data["payment_id"],
            gateway=Payment.Gateway.CARD_TO_CARD,
        )

        try:
            payment.approve_manual_payment(
                reviewed_by=request.user,
                review_note=serializer.validated_data.get("review_note", ""),
                ref_id=serializer.validated_data.get("ref_id", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PaymentStatusSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class RejectCardToCardPaymentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = RejectCardToCardPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            id=serializer.validated_data["payment_id"],
            gateway=Payment.Gateway.CARD_TO_CARD,
        )

        try:
            payment.reject_manual_payment(
                reviewed_by=request.user,
                review_note=serializer.validated_data.get("review_note", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PaymentStatusSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class PaymentStatusView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        if not request.user.is_staff and payment.user_id != request.user.id:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PaymentStatusSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class PaymentDetailView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        if not request.user.is_staff and payment.user_id != request.user.id:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class ConfirmBaleWalletPaymentView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ConfirmBaleWalletPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_id = serializer.validated_data.get("payment_id")
        telegram_payment_charge_id = serializer.validated_data["telegram_payment_charge_id"]
        provider_payment_charge_id = serializer.validated_data.get("provider_payment_charge_id", "")
        invoice_payload = serializer.validated_data["invoice_payload"]

        if payment_id is not None:
            payment = get_object_or_404(
                Payment,
                id=payment_id,
                user=request.user,
                gateway=Payment.Gateway.BALE_WALLET,
            )
        else:
            payment = get_object_or_404(
                Payment,
                user=request.user,
                gateway=Payment.Gateway.BALE_WALLET,
                wallet_payload__invoice_payload=invoice_payload,
            )

        if payment.status == Payment.Status.PAID:
            return Response(
                {"detail": "این پرداخت قبلاً تایید شده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stored_payload = payment.wallet_payload.get("invoice_payload", "")
        if stored_payload != invoice_payload:
            return Response(
                {"detail": "invoice_payload مطابقت ندارد."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = Payment.Status.PAID
        payment.ref_id = telegram_payment_charge_id
        payment.paid_at = payment.paid_at or timezone.now()

        payment.wallet_payload.update({
            "telegram_payment_charge_id": telegram_payment_charge_id,
            "provider_payment_charge_id": provider_payment_charge_id,
            "chat_id": serializer.validated_data.get("chat_id", ""),
            "message_id": serializer.validated_data.get("message_id"),
        })

        payment.verify_response = {
            "telegram_payment_charge_id": telegram_payment_charge_id,
            "provider_payment_charge_id": provider_payment_charge_id,
            "invoice_payload": invoice_payload,
            "confirmed_at": timezone.now().isoformat(),
        }

        payment.save(update_fields=[
            "status",
            "ref_id",
            "paid_at",
            "wallet_payload",
            "verify_response",
            "updated_at",
        ])

        Order.objects.get_or_create_from_payment(payment)

        return Response(
            PaymentStatusSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
