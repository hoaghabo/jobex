from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.orders.order_log.models import Order
from apps.billing.orders.order_log.serializers import OrderListSerializer, OrderSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get(self, request):
        queryset = Order.objects.all().order_by("-created_at")

        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = OrderListSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not request.user.is_staff and order.user_id != request.user.id:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK,
        )


class OrderByTrackingCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)

        if not request.user.is_staff and order.user_id != request.user.id:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK,
        )
