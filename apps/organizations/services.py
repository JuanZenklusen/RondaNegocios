"""Casos de uso de la app organizations."""

from __future__ import annotations

from .models import Organization

DEFAULT_ORGANIZATION_SLUG = "principal"


def get_default_organization() -> Organization:
    """Devuelve la organización por defecto del sistema.

    Mientras el sistema sea de una sola organización, las nuevas cuentas se
    asocian a ésta. La crea si no existe (defensivo ante entornos sin la seed).
    """
    org, _ = Organization.objects.get_or_create(
        slug=DEFAULT_ORGANIZATION_SLUG,
        defaults={
            "name": "Organización Principal",
            "description": "Organización por defecto del sistema.",
            "is_active": True,
        },
    )
    return org
