import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.notifications.models import Message, Notification
from apps.notifications.services import notify, send_message
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


def _user(email):
    return User.objects.create_user(
        email=email, password="RondaSegura123", organization=get_default_organization()
    )


def test_bell_count_in_context(client):
    u = _user("u@test.com")
    notify(recipient=u, title="A")
    client.force_login(u)
    resp = client.get(reverse("core:dashboard"))
    assert resp.context["nav_unread_notifications"] == 1


def test_open_notification_marks_read_and_redirects(client):
    u = _user("u@test.com")
    n = notify(recipient=u, title="A", url="/red/")
    client.force_login(u)
    resp = client.get(reverse("notifications:open", args=[n.pk]))
    assert resp.status_code == 302
    assert resp.url == "/red/"
    n.refresh_from_db()
    assert n.is_read is True


def test_mark_all_read_view(client):
    u = _user("u@test.com")
    notify(recipient=u, title="A")
    client.force_login(u)
    resp = client.post(reverse("notifications:mark_all_read"))
    assert resp.status_code == 302
    assert Notification.objects.filter(recipient=u, is_read=False).count() == 0


def test_send_message_view(client):
    a, b = _user("a@test.com"), _user("b@test.com")
    client.force_login(a)
    resp = client.post(reverse("notifications:send", args=[b.pk]), {"body": "Hola"})
    assert resp.status_code == 302
    assert Message.objects.filter(sender=a, recipient=b, body="Hola").exists()


def test_conversation_marks_incoming_read(client):
    a, b = _user("a@test.com"), _user("b@test.com")
    send_message(sender=a, recipient=b, body="Hola")
    client.force_login(b)
    resp = client.get(reverse("notifications:conversation", args=[a.pk]))
    assert resp.status_code == 200
    assert Message.objects.filter(recipient=b, read_at__isnull=True).count() == 0


def test_cannot_message_self(client):
    a = _user("a@test.com")
    client.force_login(a)
    client.post(reverse("notifications:send", args=[a.pk]), {"body": "yo"})
    assert not Message.objects.filter(sender=a, recipient=a).exists()
