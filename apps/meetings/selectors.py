"""Consultas de lectura de la ronda: agenda y participantes."""

from __future__ import annotations

from django.db.models import Q

from apps.companies.models import Company
from apps.events.models import Event
from apps.registrations.models import Registration

from .models import Meeting, MeetingRequest


def participating_companies(event: Event, exclude=None):
    """Empresas con inscripción confirmada en el evento."""
    company_ids = Registration.objects.filter(
        event=event, status=Registration.Status.CONFIRMED
    ).values_list("user__company__id", flat=True)
    qs = Company.objects.filter(pk__in=[c for c in company_ids if c])
    if exclude:
        qs = qs.exclude(pk=exclude.pk)
    return qs.select_related("rubro")


def company_agenda(event: Event, company: Company):
    """Devuelve la agenda de `company` en `event`: por cada bloque, la reunión
    confirmada (si hay) o si está libre."""
    meetings = {
        m.time_block_id: m
        for m in Meeting.objects.filter(event=event, status=Meeting.Status.CONFIRMED)
        .filter(Q(company_a=company) | Q(company_b=company))
        .select_related("time_block", "table", "company_a", "company_b")
    }
    agenda = []
    for block in event.time_blocks.all():
        meeting = meetings.get(block.id)
        agenda.append(
            {
                "block": block,
                "meeting": meeting,
                "other": meeting.other_company(company) if meeting else None,
            }
        )
    return agenda


def received_pending_requests(event: Event, company: Company):
    return MeetingRequest.objects.filter(
        event=event, to_company=company, status=MeetingRequest.Status.PENDING
    ).select_related("from_company", "time_block")


def sent_requests(event: Event, company: Company):
    return MeetingRequest.objects.filter(event=event, from_company=company).select_related(
        "to_company", "time_block"
    )
