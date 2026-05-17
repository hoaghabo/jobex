from rest_framework.generics import ListCreateAPIView
from .models import CompanyRole
from .serializers import CompanyRoleSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView


class CompanyRoleListCreateAPIView(ListCreateAPIView):

    queryset = CompanyRole.objects.all().order_by("name")
    serializer_class = CompanyRoleSerializer




class CompanyRoleDetailAPIView(RetrieveUpdateDestroyAPIView):

    queryset = CompanyRole.objects.all()
    serializer_class = CompanyRoleSerializer
