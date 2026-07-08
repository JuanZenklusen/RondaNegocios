import pytest
from django.urls import reverse

from apps.registrations.models import Registration
from apps.registrations.services import register_user_to_event

pytestmark = pytest.mark.django_db


def test_register_requires_login(client, make_event):
    event = make_event()
    resp = client.post(reverse("registrations:register", args=[event.pk]))
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_register_confirms_free_event(client, attendee, make_event):
    event = make_event(general_price=0)
    client.force_login(attendee)
    resp = client.post(reverse("registrations:register", args=[event.pk]))
    assert resp.status_code == 302
    assert resp.url == reverse("registrations:mine")
    reg = Registration.objects.get(event=event, user=attendee)
    assert reg.status == Registration.Status.CONFIRMED


def test_register_full_event_shows_error(client, attendee, make_event, org):
    from apps.accounts.models import User

    event = make_event(capacity=1)
    ocupa = User.objects.create_user(
        email="ocupa@test.com",
        password="RondaSegura123",
        role=User.Role.ATTENDEE,
        organization=org,
    )
    register_user_to_event(user=ocupa, event=event)
    client.force_login(attendee)
    client.post(reverse("registrations:register", args=[event.pk]), follow=True)
    assert not Registration.objects.filter(event=event, user=attendee).exists()


def test_my_registrations_lists_only_mine(client, attendee, make_event, org):
    from apps.accounts.models import User

    event = make_event()
    register_user_to_event(user=attendee, event=event)
    other = User.objects.create_user(
        email="x@test.com", password="RondaSegura123", role=User.Role.ATTENDEE, organization=org
    )
    other_event = make_event(name="Otro")
    register_user_to_event(user=other, event=other_event)

    client.force_login(attendee)
    resp = client.get(reverse("registrations:mine"))
    assert resp.status_code == 200
    assert b"Evento" in resp.content
    assert b"Otro" not in resp.content


def test_cancel_registration(client, attendee, make_event):
    event = make_event()
    reg = register_user_to_event(user=attendee, event=event)
    client.force_login(attendee)
    resp = client.post(reverse("registrations:cancel", args=[reg.pk]))
    assert resp.status_code == 302
    reg.refresh_from_db()
    assert reg.status == Registration.Status.CANCELLED


# --- Organizador ---


def test_organizer_sees_event_registrations(client, organizer, attendee, make_event):
    event = make_event()
    register_user_to_event(user=attendee, event=event)
    client.force_login(organizer)
    resp = client.get(reverse("registrations:event_registrations", args=[event.pk]))
    assert resp.status_code == 200
    assert attendee.email.encode() in resp.content


def test_organizer_approves_pending(client, organizer, attendee, make_event):
    event = make_event(requires_approval=True)
    reg = register_user_to_event(user=attendee, event=event)
    assert reg.status == Registration.Status.PENDING
    client.force_login(organizer)
    resp = client.post(reverse("registrations:respond", args=[reg.pk]), {"action": "approve"})
    assert resp.status_code == 302
    reg.refresh_from_db()
    assert reg.status == Registration.Status.CONFIRMED


def test_company_cannot_manage_registrations(client, make_event, org):
    from apps.accounts.models import User

    event = make_event()
    company = User.objects.create_user(
        email="emp@test.com", password="RondaSegura123", role=User.Role.COMPANY, organization=org
    )
    client.force_login(company)
    resp = client.get(reverse("registrations:event_registrations", args=[event.pk]))
    assert resp.status_code == 403
