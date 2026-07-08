"""Casos de uso de acreditaciones y check-in."""

from __future__ import annotations

from django.utils import timezone

from apps.registrations.models import Registration

from .models import Accreditation, Participant


class AccreditationError(Exception):
    """Error de negocio de acreditaciones."""


def _confirmed_registration(user, event) -> Registration | None:
    return Registration.objects.filter(
        event=event, user=user, status=Registration.Status.CONFIRMED
    ).first()


def get_or_create_self_accreditation(registration: Registration) -> Accreditation:
    """Credencial del propio inscripto (asistente o titular de la empresa)."""
    accreditation, _ = Accreditation.objects.get_or_create(
        registration=registration, participant=None
    )
    return accreditation


def accredit_participant(*, registration: Registration, participant: Participant) -> Accreditation:
    """Genera la credencial de un representante para un evento."""
    company = getattr(registration.user, "company", None)
    if company is None or participant.company_id != company.id:
        raise AccreditationError("El representante no pertenece a tu empresa.")
    accreditation, _ = Accreditation.objects.get_or_create(
        registration=registration, participant=participant
    )
    return accreditation


def check_in(accreditation: Accreditation) -> Accreditation:
    if accreditation.checked_in_at is None:
        accreditation.checked_in_at = timezone.now()
        accreditation.save(update_fields=["checked_in_at"])
    return accreditation


def check_out(accreditation: Accreditation) -> Accreditation:
    if accreditation.checked_in_at is None:
        raise AccreditationError("No se puede registrar egreso sin ingreso previo.")
    if accreditation.checked_out_at is None:
        accreditation.checked_out_at = timezone.now()
        accreditation.save(update_fields=["checked_out_at"])
    return accreditation
