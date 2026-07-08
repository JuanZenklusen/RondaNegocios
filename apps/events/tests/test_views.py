import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Activity, Event

pytestmark = pytest.mark.django_db


# --- Público ---------------------------------------------------------------


def test_public_list_shows_published_upcoming(client, make_event):
    make_event(name="Publicado Futuro", status=Event.Status.PUBLISHED)
    make_event(name="Borrador", status=Event.Status.DRAFT)
    resp = client.get(reverse("events:public_list"))
    assert resp.status_code == 200
    assert b"Publicado Futuro" in resp.content
    assert b"Borrador" not in resp.content


def test_public_detail_shows_program(client, make_event):
    event = make_event(name="Con Programa")
    Activity.objects.create(
        event=event,
        title="Charla de apertura",
        start=timezone.make_aware(datetime.datetime(2026, 12, 1, 10, 0)),
    )
    resp = client.get(event.get_absolute_url())
    assert resp.status_code == 200
    assert b"Charla de apertura" in resp.content


def test_draft_event_detail_is_404(client, make_event):
    event = make_event(name="Oculto", status=Event.Status.DRAFT)
    resp = client.get(event.get_absolute_url())
    assert resp.status_code == 404


# --- Organizador -----------------------------------------------------------


def test_organizer_list_requires_organization_role(client, company_user):
    client.force_login(company_user)
    resp = client.get(reverse("events:list"))
    assert resp.status_code == 403  # empresa no puede gestionar eventos


def test_organizer_can_list(client, organizer, make_event):
    make_event(name="Mi Evento")
    client.force_login(organizer)
    resp = client.get(reverse("events:list"))
    assert resp.status_code == 200
    assert b"Mi Evento" in resp.content


def test_organizer_create_event_with_activity(client, organizer):
    client.force_login(organizer)
    today = datetime.date.today()
    data = {
        "name": "Nueva Ronda",
        "event_type": Event.Type.BUSINESS_ROUND,
        "modality": Event.Modality.IN_PERSON,
        "status": Event.Status.PUBLISHED,
        "start_date": today.isoformat(),
        "end_date": (today + datetime.timedelta(days=1)).isoformat(),
        "general_price": "0",
        "meeting_duration_minutes": "30",
        "tables_count": "0",
        "activities-TOTAL_FORMS": "1",
        "activities-INITIAL_FORMS": "0",
        "activities-MIN_NUM_FORMS": "0",
        "activities-MAX_NUM_FORMS": "1000",
        "activities-0-title": "Charla inaugural",
        "activities-0-activity_type": Activity.Type.TALK,
        "activities-0-start": "2026-12-01T10:00",
        "activities-0-is_public": "on",
    }
    resp = client.post(reverse("events:create"), data)
    assert resp.status_code == 302
    event = Event.objects.get(name="Nueva Ronda")
    assert event.organization is not None
    assert event.activities.count() == 1


def test_organizer_bad_dates_rejected(client, organizer):
    client.force_login(organizer)
    today = datetime.date.today()
    data = {
        "name": "Fechas mal",
        "event_type": Event.Type.FAIR,
        "modality": Event.Modality.IN_PERSON,
        "status": Event.Status.DRAFT,
        "start_date": today.isoformat(),
        "end_date": (today - datetime.timedelta(days=2)).isoformat(),
        "general_price": "0",
        "meeting_duration_minutes": "30",
        "tables_count": "0",
        "activities-TOTAL_FORMS": "0",
        "activities-INITIAL_FORMS": "0",
        "activities-MIN_NUM_FORMS": "0",
        "activities-MAX_NUM_FORMS": "1000",
    }
    resp = client.post(reverse("events:create"), data)
    assert resp.status_code == 200
    assert not Event.objects.filter(name="Fechas mal").exists()


def test_organizer_delete_event(client, organizer, make_event):
    event = make_event(name="A borrar")
    client.force_login(organizer)
    resp = client.post(reverse("events:delete", args=[event.pk]))
    assert resp.status_code == 302
    assert not Event.objects.filter(pk=event.pk).exists()
