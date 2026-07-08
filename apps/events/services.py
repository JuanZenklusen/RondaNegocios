"""Casos de uso de la app events."""

from __future__ import annotations

import datetime

from django.db import transaction
from django.utils import timezone

from .models import Activity, Event, Table, TimeBlock


def _round_windows(event: Event) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """Ventanas horarias (inicio, fin) donde se corren las reuniones de la ronda.

    Se derivan de las actividades tipo "Ronda de negocios" del programa (así los
    bloques quedan dentro de esa franja). Si no hay ninguna con horario, se usa
    como fallback `round_start_time`/`round_end_time` en cada día del evento.
    """
    windows: list[tuple[datetime.datetime, datetime.datetime]] = []

    round_activities = event.activities.filter(
        activity_type=Activity.Type.BUSINESS_ROUND, end__isnull=False
    )
    if round_activities.exists():
        for act in round_activities:
            windows.append((timezone.localtime(act.start), timezone.localtime(act.end)))
        return windows

    if event.round_start_time and event.round_end_time:
        day = event.start_date
        while day <= event.end_date:
            windows.append(
                (
                    datetime.datetime.combine(day, event.round_start_time),
                    datetime.datetime.combine(day, event.round_end_time),
                )
            )
            day += datetime.timedelta(days=1)
    return windows


@transaction.atomic
def generate_event_schedule(event: Event) -> dict:
    """Genera las mesas y los bloques horarios de la ronda de un evento.

    - Mesas: 1..`event.tables_count`.
    - Bloques: dentro de la franja de la(s) actividad(es) "Ronda de negocios",
      en tramos de `meeting_duration_minutes`.

    Es idempotente (no duplica). Devuelve cuántos creó de cada cosa.
    """
    tables_created = 0
    for number in range(1, event.tables_count + 1):
        _, created = Table.objects.get_or_create(event=event, number=number)
        tables_created += int(created)

    blocks_created = 0
    duration = datetime.timedelta(minutes=event.meeting_duration_minutes)
    for start_dt, end_dt in _round_windows(event):
        cursor = start_dt
        while cursor + duration <= end_dt:
            slot_end = cursor + duration
            _, created = TimeBlock.objects.get_or_create(
                event=event,
                date=cursor.date(),
                start_time=cursor.time(),
                end_time=slot_end.time(),
            )
            blocks_created += int(created)
            cursor = slot_end

    return {"tables_created": tables_created, "blocks_created": blocks_created}
