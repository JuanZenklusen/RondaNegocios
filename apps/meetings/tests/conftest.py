import datetime

import pytest

from apps.accounts.models import User
from apps.companies.models import Company
from apps.events.models import Event, Table, TimeBlock
from apps.organizations.services import get_default_organization
from apps.registrations.models import Registration


@pytest.fixture
def org(db):
    return get_default_organization()


@pytest.fixture
def make_company(org):
    counter = {"n": 0}

    def _make(name=None):
        counter["n"] += 1
        n = counter["n"]
        user = User.objects.create_user(
            email=f"co{n}@test.com",
            password="RondaSegura123",
            role=User.Role.COMPANY,
            organization=org,
        )
        return Company.objects.create(
            user=user, organization=org, razon_social=name or f"Empresa {n} SA"
        )

    return _make


@pytest.fixture
def event(org):
    today = datetime.date.today()
    ev = Event.objects.create(
        organization=org,
        name="Ronda Test",
        event_type=Event.Type.BUSINESS_ROUND,
        status=Event.Status.PUBLISHED,
        start_date=today + datetime.timedelta(days=5),
        end_date=today + datetime.timedelta(days=5),
        is_public=True,
        tables_count=2,
    )
    # 2 mesas y 2 bloques
    Table.objects.create(event=ev, number=1)
    Table.objects.create(event=ev, number=2)
    TimeBlock.objects.create(
        event=ev, date=ev.start_date, start_time=datetime.time(9, 0), end_time=datetime.time(9, 30)
    )
    TimeBlock.objects.create(
        event=ev, date=ev.start_date, start_time=datetime.time(9, 30), end_time=datetime.time(10, 0)
    )
    return ev


def confirm(event, company):
    return Registration.objects.create(
        event=event, user=company.user, status=Registration.Status.CONFIRMED
    )
