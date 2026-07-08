"""Casos de uso / lógica de negocio de la app accounts.

Las vistas llaman a estos servicios; no meten lógica de negocio ellas mismas.
Ver CLAUDE.md.
"""

from __future__ import annotations

from django.db import transaction

from apps.organizations.services import get_default_organization

from .models import User


@transaction.atomic
def register_company_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    """Da de alta un usuario con rol Empresa.

    El perfil institucional de la empresa (razón social, CUIT, etc.) se completa
    en la Fase 3; acá sólo se crea la cuenta de acceso, asociada a la
    organización por defecto (sistema mono-organización por ahora).
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.COMPANY,
        organization=get_default_organization(),
    )
    return user
