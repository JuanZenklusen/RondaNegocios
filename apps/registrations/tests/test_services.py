import datetime

import pytest

from apps.events.models import Event
from apps.registrations.models import Registration
from apps.registrations.services import (
    RegistrationError,
    decide_registration,
    register_user_to_event,
)

pytestmark = pytest.mark.django_db


def test_free_event_auto_confirms(attendee, make_event):
    event = make_event(general_price=0)
    reg = register_user_to_event(user=attendee, event=event)
    assert reg.status == Registration.Status.CONFIRMED
    assert reg.payment_status == Registration.Payment.NOT_REQUIRED


def test_paid_event_marks_simulated_payment(attendee, make_event):
    event = make_event(general_price=1500)
    reg = register_user_to_event(user=attendee, event=event)
    assert reg.status == Registration.Status.CONFIRMED
    assert reg.payment_status == Registration.Payment.SIMULATED
    assert reg.amount == 1500


def test_event_requiring_approval_stays_pending(attendee, make_event):
    event = make_event(requires_approval=True)
    reg = register_user_to_event(user=attendee, event=event)
    assert reg.status == Registration.Status.PENDING


def test_duplicate_registration_returns_same(attendee, make_event):
    event = make_event()
    r1 = register_user_to_event(user=attendee, event=event)
    r2 = register_user_to_event(user=attendee, event=event)
    assert r1.pk == r2.pk
    assert Registration.objects.filter(event=event, user=attendee).count() == 1


def test_capacity_full_raises(attendee, make_event, org):
    from apps.accounts.models import User

    event = make_event(capacity=1)
    register_user_to_event(user=attendee, event=event)
    other = User.objects.create_user(
        email="otro@test.com", password="RondaSegura123", role=User.Role.ATTENDEE, organization=org
    )
    with pytest.raises(RegistrationError):
        register_user_to_event(user=other, event=event)


def test_cannot_register_to_draft(attendee, make_event):
    event = make_event(status=Event.Status.DRAFT)
    with pytest.raises(RegistrationError):
        register_user_to_event(user=attendee, event=event)


def test_cannot_register_to_finished(attendee, make_event):
    today = datetime.date.today()
    event = make_event(
        start_date=today - datetime.timedelta(days=5),
        end_date=today - datetime.timedelta(days=4),
    )
    with pytest.raises(RegistrationError):
        register_user_to_event(user=attendee, event=event)


def test_decide_registration_approves(attendee, make_event):
    event = make_event(requires_approval=True)
    reg = register_user_to_event(user=attendee, event=event)
    decide_registration(registration=reg, approve=True)
    reg.refresh_from_db()
    assert reg.status == Registration.Status.CONFIRMED
    assert reg.decided_at is not None
