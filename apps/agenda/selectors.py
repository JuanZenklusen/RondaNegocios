"""Lecturas para la agenda personal: programa del evento y agenda autocompletada."""

from __future__ import annotations

import datetime

from django.db.models import Q
from django.utils import timezone

from apps.companies.services import get_or_create_company_for_user
from apps.meetings.models import Meeting

from .models import ActivityAttendance


def attending_activity_ids(user, event) -> set[int]:
    return set(
        ActivityAttendance.objects.filter(user=user, activity__event=event).values_list(
            "activity_id", flat=True
        )
    )


def program_by_day(event):
    """Actividades del programa agrupadas por día (soporta eventos multi-día)."""
    groups: dict[datetime.date, list] = {}
    for activity in event.activities.all():
        day = timezone.localtime(activity.start).date()
        groups.setdefault(day, []).append(activity)
    return sorted(groups.items())


def personal_agenda(user, event):
    """Agenda autocompletada del usuario: actividades elegidas + reuniones
    confirmadas, en orden cronológico y agrupadas por día."""
    items = []

    attendances = ActivityAttendance.objects.filter(
        user=user, activity__event=event
    ).select_related("activity")
    for att in attendances:
        a = att.activity
        items.append(
            {
                "kind": "activity",
                "start": a.start,
                "end": a.end,
                "title": a.title,
                "type": a.get_activity_type_display(),
                "room": a.room,
                "is_public": a.is_public,
            }
        )

    if getattr(user, "is_company", False):
        company = get_or_create_company_for_user(user)
        meetings = (
            Meeting.objects.filter(event=event, status=Meeting.Status.CONFIRMED)
            .filter(Q(company_a=company) | Q(company_b=company))
            .select_related("time_block", "table", "company_a", "company_b")
        )
        for m in meetings:
            block = m.time_block
            start = timezone.make_aware(datetime.datetime.combine(block.date, block.start_time))
            end = timezone.make_aware(datetime.datetime.combine(block.date, block.end_time))
            items.append(
                {
                    "kind": "meeting",
                    "start": start,
                    "end": end,
                    "title": f"Reunión con {m.other_company(company).display_name}",
                    "table": m.table.number if m.table else None,
                }
            )

    items.sort(key=lambda it: it["start"])

    groups: dict[datetime.date, list] = {}
    for it in items:
        day = timezone.localtime(it["start"]).date()
        groups.setdefault(day, []).append(it)
    return sorted(groups.items())
