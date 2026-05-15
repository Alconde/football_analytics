from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        TACTICAL_ANALYST = "tactical_analyst", "Analista táctico"
        DATA_ANALYST = "data_analyst", "Analista de datos"
        COACH = "coach", "Entrenador"
        SCOUT = "scout", "Scout"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.COACH)
    club_name = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
# Create your models here.
