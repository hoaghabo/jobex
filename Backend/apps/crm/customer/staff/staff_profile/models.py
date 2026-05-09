from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='کاربر'
    )
    personnel_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد پرسنلی'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='سمت'
    )
    hire_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ استخدام'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'کارمند'
        verbose_name_plural = 'کارکنان'

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.mobile or str(self.user.pk)
