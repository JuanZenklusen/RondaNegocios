import datetime

import pytest

from apps.accounts.models import User
from apps.events.models import Event
from apps.organizations.services import get_default_organization


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email="org@test.com",
        password="RondaSegura123",
        role=User.Role.ORGANIZATION,
        organization=get_default_organization(),
    )


@pytest.fixture
def company_user(db):
    return User.objects.create_user(
        email="comp@test.com",
        password="RondaSegura123",
        role=User.Role.COMPANY,
        organization=get_default_organization(),
    )


@pytest.fixture
def make_event(db):
    def _make(name="Ronda 2026", status=Event.Status.PUBLISHED, **kwargs):
        today = datetime.date.today()
        defaults = {
            "organization": get_default_organization(),
            "name": name,
            "status": status,
            "start_date": today + datetime.timedelta(days=10),
            "end_date": today + datetime.timedelta(days=11),
            "is_public": True,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    return _make
