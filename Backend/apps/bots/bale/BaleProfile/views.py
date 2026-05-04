from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import BaleProfile
from .serializers import BaleProfileSerializers,BaleRegisterSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .permissions import IsBaleUserByPhoneNumber, IsBaleUserByChatIdOrPhoneNumber


    
class AdminBaleProfileListAPIView(generics.ListCreateAPIView):
    queryset = BaleProfile.objects.all()
    serializer_class = BaleProfileSerializers
    permission_classes = [IsAdminUser]

class AdminBaleProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BaleProfile.objects.all()
    serializer_class = BaleProfileSerializers
    permission_classes = [IsAdminUser]

    
class BaleMyProfileDetailsAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = BaleProfileSerializers
    permission_classes = [IsBaleUserByChatIdOrPhoneNumber]
    authentication_classes = []
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.bale_user

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()

        serializer = self.get_serializer(profile)

        return Response(
            {
                "registered": True,
                **serializer.data
            },
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()

        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    
class BaleRegisterAPIView(generics.CreateAPIView):
    serializer_class = BaleRegisterSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]
    
    

