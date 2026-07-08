import pytest
from django.urls import reverse

from apps.agenda.selectors import personal_agenda, program_by_day
from apps.agenda.services import toggle_activity_attendance

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_program_grouped_by_day(event, company_user):
    program = program_by_day(event)
    assert len(program) == 2  # dos días


def test_personal_agenda_includes_chosen_activities(event, company_user):
    confirm(event, company_user)
    toggle_activity_attendance(user=company_user, activity=event.talk)
    agenda = personal_agenda(company_user, event)
    titles = [it["title"] for _, items in agenda for it in items]
    assert "Charla pública" in titles


def test_agenda_view_requires_confirmed(client, event, company_user):
    client.force_login(company_user)
    resp = client.get(reverse("agenda:event_agenda", args=[event.slug]))
    assert resp.status_code == 302  # sin inscripción confirmada


def test_agenda_view_renders_program(client, event, company_user):
    confirm(event, company_user)
    client.force_login(company_user)
    resp = client.get(reverse("agenda:event_agenda", args=[event.slug]))
    assert resp.status_code == 200
    assert "Exposición".encode() in resp.content


def test_toggle_view(client, event, company_user):
    confirm(event, company_user)
    client.force_login(company_user)
    resp = client.post(reverse("agenda:toggle_activity", args=[event.slug, event.talk.pk]))
    assert resp.status_code == 302
    from apps.agenda.models import ActivityAttendance

    assert ActivityAttendance.objects.filter(user=company_user, activity=event.talk).exists()
