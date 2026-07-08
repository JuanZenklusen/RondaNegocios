"""Casos de uso de networking: favoritos y conexiones."""

from __future__ import annotations

from django.utils import timezone

from apps.companies.models import Company

from .models import ConnectionRequest, Favorite


def toggle_favorite(*, owner: Company, target: Company) -> bool:
    """Agrega o quita `target` de los favoritos de `owner`.

    Devuelve True si quedó guardada, False si se quitó.
    """
    if owner.pk == target.pk:
        raise ValueError("Una empresa no puede guardarse a sí misma.")
    fav = Favorite.objects.filter(owner=owner, company=target).first()
    if fav:
        fav.delete()
        return False
    Favorite.objects.create(owner=owner, company=target)
    return True


def send_connection_request(
    *, from_company: Company, to_company: Company, message=""
) -> ConnectionRequest:
    """Crea (o devuelve) una solicitud de conexión de `from_company` a `to_company`."""
    if from_company.pk == to_company.pk:
        raise ValueError("Una empresa no puede conectarse consigo misma.")
    conn, created = ConnectionRequest.objects.get_or_create(
        from_company=from_company,
        to_company=to_company,
        defaults={"message": message},
    )
    if created:
        from django.urls import reverse

        from apps.notifications.services import notify

        notify(
            recipient=to_company.user,
            title=f"Nueva solicitud de conexión de {from_company.display_name}",
            url=reverse("networking:connections"),
        )
    return conn


def respond_connection_request(*, connection: ConnectionRequest, accept: bool) -> ConnectionRequest:
    """Acepta o rechaza una solicitud pendiente."""
    connection.status = (
        ConnectionRequest.Status.ACCEPTED if accept else ConnectionRequest.Status.REJECTED
    )
    connection.responded_at = timezone.now()
    connection.save(update_fields=["status", "responded_at"])
    return connection
