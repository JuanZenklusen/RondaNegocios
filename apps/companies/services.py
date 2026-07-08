"""Casos de uso de la app companies."""

from __future__ import annotations

from apps.accounts.models import User

from .models import Company


def get_or_create_company_for_user(user: User) -> Company:
    """Devuelve el perfil de empresa del usuario, creándolo vacío si no existe.

    Permite que las cuentas creadas antes de tener perfil (Fase 1) obtengan uno
    la primera vez que entran a "Perfil Empresa". La empresa hereda la
    organización del usuario.
    """
    company = Company.objects.filter(user=user).first()
    if company is not None:
        return company
    return Company.objects.create(
        user=user,
        organization=user.organization,
        razon_social=user.get_full_name() or user.email.split("@")[0],
    )
