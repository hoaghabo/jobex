from django.urls import path

from apps.billing.orders.order_log.views import (
    OrderByTrackingCodeView,
    OrderDetailView,
    OrderListView,
)

urlpatterns = [
    path(
        "",
        OrderListView.as_view(),
        name="billing-order-list",
    ),

    path(
        "<int:order_id>/",
        OrderDetailView.as_view(),
        name="billing-order-detail",
    ),

    path(
        "tracking/<str:tracking_code>/",
        OrderByTrackingCodeView.as_view(),
        name="billing-order-by-tracking-code",
    ),
]
