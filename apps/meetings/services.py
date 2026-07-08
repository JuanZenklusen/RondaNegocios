"""Lógica de negocio de la ronda de reuniones.

Reglas clave:
- Una empresa no puede tener dos reuniones confirmadas en el mismo bloque.
- Una mesa no puede tener dos reuniones en el mismo bloque.
- Al aceptar una solicitud se asigna automáticamente una mesa libre.
"""

from __future__ import annotations

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.events.models import Event, Table, TimeBlock

from .models import Meeting, MeetingRequest


class MeetingError(Exception):
    """Error de negocio al gestionar reuniones (conflicto, sin mesas, etc.)."""


def _company_busy_at(event: Event, company, time_block: TimeBlock, exclude_meeting=None) -> bool:
    qs = Meeting.objects.filter(
        event=event,
        time_block=time_block,
        status=Meeting.Status.CONFIRMED,
    ).filter(Q(company_a=company) | Q(company_b=company))
    if exclude_meeting:
        qs = qs.exclude(pk=exclude_meeting.pk)
    return qs.exists()


def _free_table(event: Event, time_block: TimeBlock) -> Table | None:
    used_ids = Meeting.objects.filter(
        event=event, time_block=time_block, status=Meeting.Status.CONFIRMED
    ).values_list("table_id", flat=True)
    return event.tables.exclude(pk__in=used_ids).order_by("number").first()


@transaction.atomic
def request_meeting(
    *, event: Event, from_company, to_company, time_block: TimeBlock, message=""
) -> MeetingRequest:
    """Crea una solicitud de reunión de `from_company` a `to_company`."""
    if from_company.pk == to_company.pk:
        raise MeetingError("Una empresa no puede reunirse consigo misma.")
    if time_block.event_id != event.id:
        raise MeetingError("El bloque horario no pertenece a este evento.")

    # ¿Ya hay una reunión confirmada entre ambas en este evento?
    existing_meeting = Meeting.objects.filter(event=event, status=Meeting.Status.CONFIRMED).filter(
        Q(company_a=from_company, company_b=to_company)
        | Q(company_a=to_company, company_b=from_company)
    )
    if existing_meeting.exists():
        raise MeetingError("Ya tienen una reunión confirmada en este evento.")

    request, created = MeetingRequest.objects.get_or_create(
        from_company=from_company,
        to_company=to_company,
        time_block=time_block,
        defaults={"event": event, "message": message},
    )
    if not created and request.status != MeetingRequest.Status.PENDING:
        # Reactiva una solicitud previamente rechazada/cancelada.
        request.status = MeetingRequest.Status.PENDING
        request.message = message
        request.responded_at = None
        request.save()

    from django.urls import reverse

    from apps.notifications.services import notify

    notify(
        recipient=to_company.user,
        title=f"Nueva solicitud de reunión de {from_company.display_name}",
        message=f"Para el horario {time_block}.",
        url=reverse("meetings:round", args=[event.slug]),
    )
    return request


@transaction.atomic
def accept_meeting_request(*, request: MeetingRequest) -> Meeting:
    """Acepta la solicitud: valida conflictos, asigna mesa y crea la reunión."""
    block = request.time_block
    event = request.event

    if _company_busy_at(event, request.from_company, block):
        raise MeetingError("La empresa solicitante ya tiene una reunión en ese horario.")
    if _company_busy_at(event, request.to_company, block):
        raise MeetingError("Tenés otra reunión confirmada en ese horario.")

    table = _free_table(event, block)
    if table is None:
        raise MeetingError("No hay mesas disponibles en ese bloque horario.")

    meeting = Meeting.objects.create(
        event=event,
        request=request,
        company_a=request.from_company,
        company_b=request.to_company,
        time_block=block,
        table=table,
        status=Meeting.Status.CONFIRMED,
    )
    request.status = MeetingRequest.Status.ACCEPTED
    request.responded_at = timezone.now()
    request.save(update_fields=["status", "responded_at"])

    from django.urls import reverse

    from apps.notifications.models import Notification
    from apps.notifications.services import notify

    notify(
        recipient=request.from_company.user,
        title=f"Reunión confirmada con {request.to_company.display_name}",
        message=f"{block} · Mesa {table.number}.",
        url=reverse("meetings:round", args=[event.slug]),
        level=Notification.Level.SUCCESS,
        email=True,
    )
    return meeting


@transaction.atomic
def reject_meeting_request(*, request: MeetingRequest) -> MeetingRequest:
    request.status = MeetingRequest.Status.REJECTED
    request.responded_at = timezone.now()
    request.save(update_fields=["status", "responded_at"])
    return request


@transaction.atomic
def cancel_meeting(*, meeting: Meeting) -> Meeting:
    """Cancela una reunión confirmada (libera la mesa y el bloque)."""
    meeting.status = Meeting.Status.CANCELLED
    meeting.save(update_fields=["status"])
    if meeting.request_id:
        MeetingRequest.objects.filter(pk=meeting.request_id).update(
            status=MeetingRequest.Status.CANCELLED
        )
    return meeting
