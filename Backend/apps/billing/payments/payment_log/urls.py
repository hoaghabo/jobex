from django.urls import path

from apps.billing.payments.payment_log.views import (
    ApproveCardToCardPaymentView,
    CreatePaymentView,
    PaymentDetailView,
    PaymentStatusView,
    RejectCardToCardPaymentView,
    SubmitCardToCardReceiptView,
    ConfirmBaleWalletPaymentView,
    ZarinpalCallbackView,
)

urlpatterns = [
    path(
        "create/",
        CreatePaymentView.as_view(),
        name="billing-payment-create",
    ),

    path(
        "zarinpal/callback/",
        ZarinpalCallbackView.as_view(),
        name="billing-zarinpal-callback",
    ),

    path(
        "card-to-card/submit-receipt/",
        SubmitCardToCardReceiptView.as_view(),
        name="billing-card-to-card-submit-receipt",
    ),

    path(
        "card-to-card/approve/",
        ApproveCardToCardPaymentView.as_view(),
        name="billing-card-to-card-approve",
    ),

    path(
        "card-to-card/reject/",
        RejectCardToCardPaymentView.as_view(),
        name="billing-card-to-card-reject",
    ),
    
    path(
        "bale-wallet/confirm/",
        ConfirmBaleWalletPaymentView.as_view(),
        name="billing-card-to-card-reject",
    ),


    path(
        "<int:payment_id>/status/",
        PaymentStatusView.as_view(),
        name="billing-payment-status",
    ),

    path(
        "<int:payment_id>/",
        PaymentDetailView.as_view(),
        name="billing-payment-detail",
    ),
]
