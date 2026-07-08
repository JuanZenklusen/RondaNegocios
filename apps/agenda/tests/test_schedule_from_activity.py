import pytest
from django.utils import timezone

from apps.events.services import generate_event_schedule

pytestmark = pytest.mark.django_db


def test_blocks_generated_within_round_activity_window(event):
    """Los bloques se generan dentro de la franja de la actividad
    'Ronda de negocios' (11:00–13:00, 30 min = 4 bloques)."""
    result = generate_event_schedule(event)
    assert result["blocks_created"] == 4
    blocks = list(event.time_blocks.all())
    assert len(blocks) == 4
    # Todos dentro de 11:00–13:00.
    assert str(blocks[0].start_time) == "11:00:00"
    assert str(blocks[-1].end_time) == "13:00:00"
    # En el día de la actividad ronda.
    round_day = timezone.localtime(event.round.start).date()
    assert all(b.date == round_day for b in blocks)
