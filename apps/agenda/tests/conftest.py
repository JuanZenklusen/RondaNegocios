import datetime

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Activity, Event
from apps.organizations.services import get_default_organization
from apps.registrations.models import Registration


@pytest.fixture
def org(db):
    return get_default_organization()


@pytest.fixture
def event(org):
    today = datetime.date.today()
    ev = Event.objects.create(
        organization=org,
        name="Ronda Multi",
        event_type=Event.Type.BUSINESS_ROUND,
        status=Event.Status.PUBLISHED,
        start_date=today + datetime.timedelta(days=5),
        end_date=today + datetime.timedelta(days=6),
        is_public=True,
        meeting_duration_minutes=30,
        tables_count=2,
    )

    def at(day_offset, hour):
        day = ev.start_date + datetime.timedelta(days=day_offset)
        return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour)))

    ev.talk = Activity.objects.create(
        event=ev,
        title="Charla pública",
        activity_type=Activity.Type.TALK,
        start=at(0, 10),
        end=at(0, 11),
        is_public=True,
    )
    ev.round = Activity.objects.create(
        event=ev,
        title="Ronda de negocios (mesas)",
        activity_type=Activity.Type.BUSINESS_ROUND,
        start=at(0, 11),
        end=at(0, 13),
        is_public=False,
    )
    ev.day2 = Activity.objects.create(
        event=ev,
        title="Exposición",
        activity_type=Activity.Type.EXHIBITION,
        start=at(1, 10),
        end=at(1, 12),
        is_public=True,
    )
    return ev


@pytest.fixture
def company_user(org):
    return User.objects.create_user(
        email="co@test.com",
        password="RondaSegura123",
        role=User.Role.COMPANY,
        organization=org,
    )


@pytest.fixture
def attendee_user(org):
    return User.objects.create_user(
        email="as@test.com",
        password="RondaSegura123",
        role=User.Role.ATTENDEE,
        organization=org,
    )


def confirm(event, user):
    return Registration.objects.create(event=event, user=user, status=Registration.Status.CONFIRMED)
