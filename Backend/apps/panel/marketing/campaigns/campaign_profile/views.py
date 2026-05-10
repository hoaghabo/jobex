from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        هر کاربر فقط کمپین‌های خودش را ببیند.
        """
        return Campaign.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        موقع ساخت کمپین، owner برابر کاربر لاگین‌شده قرار می‌گیرد.
        """
        serializer.save(owner=self.request.user)
