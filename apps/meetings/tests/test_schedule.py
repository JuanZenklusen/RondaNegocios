import datetime

import pytest

from apps.events.models import Event
from apps.events.services import generate_event_schedule
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


def test_generate_schedule_creates_tables_and_blocks():
    org = get_default_organization()
    today = datetime.date.today()
    event = Event.objects.create(
        organization=org,
        name="Ronda",
        start_date=today,
        end_date=today,  # un solo día
        tables_count=3,
        meeting_duration_minutes=30,
        round_start_time=datetime.time(9, 0),
        round_end_time=datetime.time(11, 0),  # 4 bloques de 30 min
    )
    result = generate_event_schedule(event)
    assert result["tables_created"] == 3
    assert result["blocks_created"] == 4
    assert event.tables.count() == 3
    assert event.time_blocks.count() == 4


def test_generate_schedule_is_idempotent():
    org = get_default_organization()
    today = datetime.date.today()
    event = Event.objects.create(
        organization=org,
        name="Ronda",
        start_date=today,
        end_date=today,
        tables_count=2,
        round_start_time=datetime.time(9, 0),
        round_end_time=datetime.time(10, 0),
    )
    generate_event_schedule(event)
    result2 = generate_event_schedule(event)
    assert result2["tables_created"] == 0
    assert result2["blocks_created"] == 0
    assert event.tables.count() == 2
