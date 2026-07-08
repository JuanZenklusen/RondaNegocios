import datetime

import pytest

from apps.accounts.models import User
from apps.companies.models import Company
from apps.events.models import Event, TimeBlock
from apps.meetings.services import request_meeting
from apps.notifications.models import Notification
from apps.organizations.services import get_default_organization
from apps.registrations.models import Registration
from apps.registrations.services import decide_registration

pytestmark = pytest.mark.django_db


def _company(email):
    org = get_default_organization()
    user = User.objects.create_user(
        email=email, password="RondaSegura123", role=User.Role.COMPANY, organization=org
    )
    return Company.objects.create(user=user, organization=org, razon_social=email)


def test_meeting_request_notifies_target(db):
    org = get_default_organization()
    today = datetime.date.today()
    event = Event.objects.create(
        organization=org,
        name="Ronda",
        status=Event.Status.PUBLISHED,
        start_date=today,
        end_date=today,
        tables_count=1,
    )
    block = TimeBlock.objects.create(
        event=event,
        date=today,
        start_time=datetime.time(9, 0),
        end_time=datetime.time(9, 30),
    )
    a, b = _company("a@test.com"), _company("b@test.com")
    request_meeting(event=event, from_company=a, to_company=b, time_block=block)
    assert Notification.objects.filter(recipient=b.user).exists()


def test_registration_approval_notifies_and_emails(db):
    from django.core import mail

    org = get_default_organization()
    today = datetime.date.today()
    event = Event.objects.create(
        organization=org,
        name="Evento",
        status=Event.Status.PUBLISHED,
        start_date=today,
        end_date=today,
    )
    user = User.objects.create_user(
        email="p@test.com",
        password="RondaSegura123",
        role=User.Role.ATTENDEE,
        organization=org,
    )
    reg = Registration.objects.create(event=event, user=user, status=Registration.Status.PENDING)
    decide_registration(registration=reg, approve=True)
    assert Notification.objects.filter(recipient=user).exists()
    assert len(mail.outbox) == 1
