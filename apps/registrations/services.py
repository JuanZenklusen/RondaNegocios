"""Casos de uso de inscripciones a eventos.

El pago es SIMULADO por ahora: los eventos pagos marcan la inscripción como
`payment=SIMULATED` sin pasar por una pasarela real (Mercado Pago = fase futura).
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.events.models import Event

from .models import Registration


class RegistrationError(Exception):
    """Error de negocio al inscribirse (evento cerrado, cupo lleno, etc.)."""


@transaction.atomic
def register_user_to_event(*, user, event: Event) -> Registration:
    """Inscribe a `user` en `event` aplicando las reglas de negocio.

    - El evento debe estar publicado y no finalizado.
    - No se puede inscribir dos veces (si ya tiene una inscripción activa, la
      devuelve tal cual).
    - Respeta el cupo (`event.capacity`).
    - Estado inicial: PENDIENTE si el evento requiere aprobación, si no CONFIRMADA.
    - Pago: sin costo si es gratis; simulado si tiene precio.
    """
    if event.status != Event.Status.PUBLISHED:
        raise RegistrationError("Este evento no está disponible para inscripción.")
    if not event.is_upcoming:
        raise RegistrationError("Este evento ya finalizó.")

    existing = Registration.objects.filter(event=event, user=user).first()
    if existing and existing.is_active:
        return existing

    # Bloquea el evento para contar cupos de forma consistente.
    locked = Event.objects.select_for_update().get(pk=event.pk)
    if locked.is_full:
        raise RegistrationError("El evento agotó su cupo.")

    status = (
        Registration.Status.PENDING if locked.requires_approval else Registration.Status.CONFIRMED
    )
    if locked.is_free:
        payment = Registration.Payment.NOT_REQUIRED
    else:
        payment = Registration.Payment.SIMULATED  # pago simulado

    registration, _ = Registration.objects.update_or_create(
        event=locked,
        user=user,
        defaults={
            "status": status,
            "payment_status": payment,
            "amount": locked.general_price,
            "decided_at": None if status == Registration.Status.PENDING else timezone.now(),
        },
    )
    return registration


def decide_registration(*, registration: Registration, approve: bool) -> Registration:
    """Aprueba o rechaza una inscripción pendiente (organizador)."""
    registration.status = Registration.Status.CONFIRMED if approve else Registration.Status.REJECTED
    registration.decided_at = timezone.now()
    registration.save(update_fields=["status", "decided_at"])

    from apps.notifications.models import Notification
    from apps.notifications.services import notify

    notify(
        recipient=registration.user,
        title=(
            f"Inscripción aprobada: {registration.event.name}"
            if approve
            else f"Inscripción rechazada: {registration.event.name}"
        ),
        url=registration.event.get_absolute_url(),
        level=Notification.Level.SUCCESS if approve else Notification.Level.WARNING,
        email=True,
    )
    return registration


def cancel_registration(*, registration: Registration) -> Registration:
    """El propio usuario cancela su inscripción."""
    registration.status = Registration.Status.CANCELLED
    registration.decided_at = timezone.now()
    registration.save(update_fields=["status", "decided_at"])
    return registration
