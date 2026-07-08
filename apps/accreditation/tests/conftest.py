import datetime

import pytest

from apps.accounts.models import User
from apps.companies.models import Company
from apps.events.models import Event
from apps.organizations.services import get_default_organization
from apps.registrations.models import Registration


@pytest.fixture
def org(db):
    return get_default_organization()


@pytest.fixture
def event(org):
    today = datetime.date.today()
    return Event.objects.create(
        organization=org,
        name="Evento Acred",
        status=Event.Status.PUBLISHED,
        start_date=today + datetime.timedelta(days=5),
        end_date=today + datetime.timedelta(days=5),
        is_public=True,
        location="Centro",
    )


@pytest.fixture
def company_user(org):
    user = User.objects.create_user(
        email="co@test.com",
        password="RondaSegura123",
        role=User.Role.COMPANY,
        organization=org,
    )
    Company.objects.create(user=user, organization=org, razon_social="Acme SA")
    return user


@pytest.fixture
def attendee_user(org):
    return User.objects.create_user(
        email="as@test.com",
        password="RondaSegura123",
        role=User.Role.ATTENDEE,
        organization=org,
    )


@pytest.fixture
def organizer(org):
    return User.objects.create_user(
        email="org@test.com",
        password="RondaSegura123",
        role=User.Role.ORGANIZATION,
        organization=org,
    )


def confirm(event, user):
    return Registration.objects.create(event=event, user=user, status=Registration.Status.CONFIRMED)
