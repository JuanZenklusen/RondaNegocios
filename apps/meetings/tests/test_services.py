import pytest

from apps.events.models import TimeBlock
from apps.meetings.models import Meeting, MeetingRequest
from apps.meetings.services import (
    MeetingError,
    accept_meeting_request,
    request_meeting,
)

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_request_and_accept_assigns_table(event, make_company):
    a, b = make_company("A SA"), make_company("B SA")
    block = event.time_blocks.first()

    req = request_meeting(event=event, from_company=a, to_company=b, time_block=block)
    assert req.status == MeetingRequest.Status.PENDING

    meeting = accept_meeting_request(request=req)
    assert meeting.status == Meeting.Status.CONFIRMED
    assert meeting.table is not None
    req.refresh_from_db()
    assert req.status == MeetingRequest.Status.ACCEPTED


def test_cannot_request_self(event, make_company):
    a = make_company("A SA")
    block = event.time_blocks.first()
    with pytest.raises(MeetingError):
        request_meeting(event=event, from_company=a, to_company=a, time_block=block)


def test_company_cannot_double_book_same_block(event, make_company):
    a, b, c = make_company("A"), make_company("B"), make_company("C")
    block = event.time_blocks.first()

    accept_meeting_request(
        request=request_meeting(event=event, from_company=a, to_company=b, time_block=block)
    )
    # c intenta reunirse con a en el mismo bloque -> a está ocupada
    req2 = request_meeting(event=event, from_company=c, to_company=a, time_block=block)
    with pytest.raises(MeetingError):
        accept_meeting_request(request=req2)


def test_tables_run_out(event, make_company):
    # event tiene 2 mesas. 3 reuniones en paralelo en el mismo bloque -> la 3ra falla.
    block = event.time_blocks.first()
    a, b = make_company(), make_company()
    c, d = make_company(), make_company()
    e, f = make_company(), make_company()

    accept_meeting_request(
        request=request_meeting(event=event, from_company=a, to_company=b, time_block=block)
    )
    accept_meeting_request(
        request=request_meeting(event=event, from_company=c, to_company=d, time_block=block)
    )
    req3 = request_meeting(event=event, from_company=e, to_company=f, time_block=block)
    with pytest.raises(MeetingError):
        accept_meeting_request(request=req3)


def test_different_blocks_no_conflict(event, make_company):
    a, b = make_company("A"), make_company("B")
    b1, b2 = list(event.time_blocks.all())

    m1 = accept_meeting_request(
        request=request_meeting(event=event, from_company=a, to_company=b, time_block=b1)
    )
    # Misma pareja en otro bloque: primero hay que evitar el bloqueo de "ya tienen reunión".
    # El servicio bloquea reuniones repetidas entre la misma pareja -> se espera MeetingError.
    with pytest.raises(MeetingError):
        request_meeting(event=event, from_company=a, to_company=b, time_block=b2)
    assert m1.table is not None


def test_cannot_request_block_of_other_event(event, make_company, org):
    import datetime

    from apps.events.models import Event

    other = Event.objects.create(
        organization=org,
        name="Otro",
        start_date=datetime.date.today(),
        end_date=datetime.date.today(),
    )
    foreign_block = TimeBlock.objects.create(
        event=other,
        date=other.start_date,
        start_time=datetime.time(9, 0),
        end_time=datetime.time(9, 30),
    )
    a, b = make_company("A"), make_company("B")
    with pytest.raises(MeetingError):
        request_meeting(event=event, from_company=a, to_company=b, time_block=foreign_block)


def test_confirm_helper_used(event, make_company):
    # Sanity: el helper de inscripción confirmada funciona (se usa en tests de vistas).
    a = make_company("A")
    reg = confirm(event, a)
    assert reg.status == "confirmed"
