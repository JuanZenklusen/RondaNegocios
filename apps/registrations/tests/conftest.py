import datetime

import pytest

from apps.accounts.models import User
from apps.events.models import Event
from apps.organizations.services import get_default_organization


@pytest.fixture
def org(db):
    return get_default_organization()


@pytest.fixture
def attendee(org):
    return User.objects.create_user(
        email="asis@test.com",
        password="RondaSegura123",
        role=User.Role.ATTENDEE,
        organization=org,
    )


@pytest.fixture
def organizer(org):
    return User.objects.create_user(
        email="orga@test.com",
        password="RondaSegura123",
        role=User.Role.ORGANIZATION,
        organization=org,
    )


@pytest.fixture
def make_event(org):
    def _make(name="Evento", **kwargs):
        today = datetime.date.today()
        defaults = {
            "organization": org,
            "name": name,
            "status": Event.Status.PUBLISHED,
            "start_date": today + datetime.timedelta(days=10),
            "end_date": today + datetime.timedelta(days=11),
            "is_public": True,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    return _make
