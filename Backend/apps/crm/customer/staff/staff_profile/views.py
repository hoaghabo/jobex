from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Employee
from .serializers import EmployeeSerializer, EmployeeLoginSerializer

User = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user').all().order_by('-id')
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class EmployeeLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return Response(
                {'detail': 'شماره موبایل یا رمز عبور اشتباه است'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'شماره موبایل یا رمز عبور اشتباه است'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'detail': 'حساب کاربری غیرفعال است'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response(
                {'detail': 'برای این کاربر پروفایل کارمندی ثبت نشده است'},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'ورود موفقیت‌آمیز بود',
            'employee': {
                'id': employee.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile': user.mobile,
                'personnel_code': employee.personnel_code,
                'position': employee.position,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
