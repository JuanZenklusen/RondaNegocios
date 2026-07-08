import pytest
from django.core import mail

from apps.accounts.models import User
from apps.notifications.models import Message, Notification
from apps.notifications.selectors import inbox
from apps.notifications.services import mark_all_read, notify, send_message
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


def _user(email):
    return User.objects.create_user(
        email=email, password="RondaSegura123", organization=get_default_organization()
    )


def test_notify_creates_notification():
    u = _user("u@test.com")
    n = notify(recipient=u, title="Hola", message="Mundo")
    assert Notification.objects.filter(recipient=u).count() == 1
    assert n.is_read is False


def test_notify_with_email_sends_console_mail():
    u = _user("u@test.com")
    notify(recipient=u, title="Reunión confirmada", email=True)
    assert len(mail.outbox) == 1
    assert "u@test.com" in mail.outbox[0].to


def test_mark_all_read():
    u = _user("u@test.com")
    notify(recipient=u, title="A")
    notify(recipient=u, title="B")
    mark_all_read(u)
    assert Notification.objects.filter(recipient=u, is_read=False).count() == 0


def test_send_message_notifies_recipient():
    a, b = _user("a@test.com"), _user("b@test.com")
    send_message(sender=a, recipient=b, body="Hola, ¿coordinamos?")
    assert Message.objects.filter(sender=a, recipient=b).count() == 1
    # El destinatario recibe una notificación.
    assert Notification.objects.filter(recipient=b).exists()


def test_inbox_groups_by_other_and_counts_unread():
    a, b = _user("a@test.com"), _user("b@test.com")
    send_message(sender=a, recipient=b, body="1")
    send_message(sender=a, recipient=b, body="2")
    convs = inbox(b)
    assert len(convs) == 1
    assert convs[0]["other"] == a
    assert convs[0]["unread"] == 2
