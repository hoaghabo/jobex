from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class AccessLevel(models.IntegerChoices):
        VIEWER = 1, "Viewer"
        OPERATOR = 2, "Operator"
        MANAGER = 3, "Manager"
        ADMIN = 4, "Admin"
        OWNER = 5, "Owner"

    access_level = models.PositiveSmallIntegerField(
        choices=AccessLevel.choices,
        default=AccessLevel.VIEWER,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    def has_access_level(self, level: int) -> bool:
        return self.access_level >= level

    def __str__(self):
        return self.username
