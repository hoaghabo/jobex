from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class AccountManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(phone_number, password, **extra_fields)


class Accounts(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = "male", "مرد"
        FEMALE = "female", "زن"
        OTHER = "other", "سایر"

    username = None
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    display_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="شماره همراه")
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="شماره تماس")
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
        verbose_name="جنسیت"
    )
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name="استان")
    day_birthdate = models.IntegerField(null=True, blank=True)
    month_birthdate = models.IntegerField(null=True, blank=True)
    year_birthdate = models.IntegerField(null=True, blank=True)

    is_phone_verified = models.BooleanField(default=False)
    is_registration_completed = models.BooleanField(default=False)
    is_bot_bale_member = models.BooleanField(default=False)
    is_jobseeker_member = models.BooleanField(default=False)
    is_company_member = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.phone_number
