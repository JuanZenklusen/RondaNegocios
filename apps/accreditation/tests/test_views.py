import pytest
from django.urls import reverse

from apps.accreditation.models import Accreditation, Participant
from apps.accreditation.services import get_or_create_self_accreditation

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_credentials_creates_self_accreditation(client, attendee_user, event):
    confirm(event, attendee_user)
    client.force_login(attendee_user)
    resp = client.get(reverse("accreditation:credentials"))
    assert resp.status_code == 200
    assert Accreditation.objects.filter(registration__user=attendee_user, participant=None).exists()


def test_qr_returns_png(client, attendee_user, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    client.force_login(attendee_user)
    resp = client.get(reverse("accreditation:qr", args=[acc.code]))
    assert resp.status_code == 200
    assert resp["Content-Type"] == "image/png"
    assert resp.content[:8] == b"\x89PNG\r\n\x1a\n"  # firma PNG


def test_qr_hidden_from_strangers(client, attendee_user, company_user, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    client.force_login(company_user)  # no es el titular ni organizador
    resp = client.get(reverse("accreditation:qr", args=[acc.code]))
    assert resp.status_code == 404


def test_company_adds_participant(client, company_user, event):
    confirm(event, company_user)
    client.force_login(company_user)
    resp = client.post(
        reverse("accreditation:participant_create"),
        {"first_name": "Ana", "last_name": "Pérez", "cargo": "CEO"},
    )
    assert resp.status_code == 302
    assert Participant.objects.filter(company=company_user.company, first_name="Ana").exists()


def test_organizer_checkin_flow(client, attendee_user, organizer, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    client.force_login(organizer)
    # GET muestra la credencial
    assert client.get(reverse("accreditation:checkin", args=[acc.code])).status_code == 200
    # POST registra ingreso
    resp = client.post(reverse("accreditation:checkin", args=[acc.code]), {"action": "checkin"})
    assert resp.status_code == 302
    acc.refresh_from_db()
    assert acc.checked_in_at is not None


def test_company_cannot_checkin(client, attendee_user, company_user, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    client.force_login(company_user)
    resp = client.get(reverse("accreditation:checkin", args=[acc.code]))
    assert resp.status_code == 403
