import pytest

from apps.agenda.models import ActivityAttendance
from apps.agenda.services import AgendaError, toggle_activity_attendance

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_toggle_adds_then_removes(event, company_user):
    confirm(event, company_user)
    assert toggle_activity_attendance(user=company_user, activity=event.talk) is True
    assert ActivityAttendance.objects.filter(user=company_user, activity=event.talk).exists()
    assert toggle_activity_attendance(user=company_user, activity=event.talk) is False
    assert not ActivityAttendance.objects.filter(user=company_user, activity=event.talk).exists()


def test_requires_confirmed_registration(event, company_user):
    with pytest.raises(AgendaError):
        toggle_activity_attendance(user=company_user, activity=event.talk)


def test_attendee_cannot_join_non_public_activity(event, attendee_user):
    confirm(event, attendee_user)
    with pytest.raises(AgendaError):
        toggle_activity_attendance(user=attendee_user, activity=event.round)


def test_attendee_can_join_public_activity(event, attendee_user):
    confirm(event, attendee_user)
    assert toggle_activity_attendance(user=attendee_user, activity=event.talk) is True
