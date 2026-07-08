from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Administrador"
        ORGANIZATION = "organization", "Organización"
        COMPANY = "company", "Empresa"
        REPRESENTATIVE = "representative", "Representante"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.COMPANY)

    def __str__(self):
        return self.username
