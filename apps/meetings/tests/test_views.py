import pytest
from django.urls import reverse

from apps.meetings.models import Meeting, MeetingRequest
from apps.meetings.services import request_meeting

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_round_requires_confirmed_registration(client, event, make_company):
    a = make_company("A")
    client.force_login(a.user)
    resp = client.get(reverse("meetings:round", args=[event.slug]))
    # Sin inscripción confirmada -> redirige al detalle del evento
    assert resp.status_code == 302
    assert event.get_absolute_url() in resp.url


def test_round_accessible_when_confirmed(client, event, make_company):
    a = make_company("A")
    confirm(event, a)
    client.force_login(a.user)
    resp = client.get(reverse("meetings:round", args=[event.slug]))
    assert resp.status_code == 200


def test_request_meeting_via_view(client, event, make_company):
    a, b = make_company("A SA"), make_company("B SA")
    confirm(event, a)
    confirm(event, b)
    block = event.time_blocks.first()
    client.force_login(a.user)
    resp = client.post(
        reverse("meetings:request", args=[event.slug]),
        {"to_company": b.pk, "time_block": block.pk, "message": "Hola"},
    )
    assert resp.status_code == 302
    assert MeetingRequest.objects.filter(from_company=a, to_company=b).exists()


def test_accept_request_via_view_creates_meeting(client, event, make_company):
    a, b = make_company("A SA"), make_company("B SA")
    confirm(event, a)
    confirm(event, b)
    block = event.time_blocks.first()
    req = request_meeting(event=event, from_company=a, to_company=b, time_block=block)

    client.force_login(b.user)
    resp = client.post(reverse("meetings:respond", args=[req.pk]), {"action": "accept"})
    assert resp.status_code == 302
    assert Meeting.objects.filter(event=event, status=Meeting.Status.CONFIRMED).exists()


def test_cannot_respond_others_request(client, event, make_company):
    a, b, c = make_company("A"), make_company("B"), make_company("C")
    confirm(event, a)
    confirm(event, b)
    block = event.time_blocks.first()
    req = request_meeting(event=event, from_company=a, to_company=b, time_block=block)

    confirm(event, c)
    client.force_login(c.user)  # c no es la destinataria
    resp = client.post(reverse("meetings:respond", args=[req.pk]), {"action": "accept"})
    assert resp.status_code == 404
