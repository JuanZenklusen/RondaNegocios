"""Casos de uso de la agenda personal del inscripto."""

from __future__ import annotations

from apps.events.models import Activity
from apps.registrations.models import Registration

from .models import ActivityAttendance


class AgendaError(Exception):
    """Error de negocio al gestionar la agenda personal."""


def _is_registered(user, event) -> bool:
    return Registration.objects.filter(
        event=event, user=user, status=Registration.Status.CONFIRMED
    ).exists()


def toggle_activity_attendance(*, user, activity: Activity) -> bool:
    """Agrega o quita la asistencia del usuario a una actividad.

    Devuelve True si quedó anotado, False si se quitó.
    """
    event = activity.event
    if not _is_registered(user, event):
        raise AgendaError("Necesitás estar inscripto y confirmado en el evento.")
    if getattr(user, "is_attendee", False) and not activity.is_public:
        raise AgendaError("Esta actividad es solo para empresas participantes.")

    attendance = ActivityAttendance.objects.filter(user=user, activity=activity).first()
    if attendance:
        attendance.delete()
        return False
    ActivityAttendance.objects.create(user=user, activity=activity)
    return True
