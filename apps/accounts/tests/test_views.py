import pytest
from django.core import mail
from django.urls import reverse

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_register_creates_user_and_logs_in(client):
    resp = client.post(
        reverse("accounts:register"),
        {
            "email": "nueva@test.com",
            "first_name": "Ana",
            "last_name": "Pérez",
            "password1": "RondaSegura123",
            "password2": "RondaSegura123",
        },
    )
    assert resp.status_code == 302
    assert resp.url == reverse("core:dashboard")
    user = User.objects.get(email="nueva@test.com")
    assert user.role == User.Role.COMPANY
    # Quedó logueado en la sesión.
    assert "_auth_user_id" in client.session


def test_register_rejects_duplicate_email(client):
    User.objects.create_user(email="dup@test.com", password="RondaSegura123")
    resp = client.post(
        reverse("accounts:register"),
        {
            "email": "dup@test.com",
            "password1": "RondaSegura123",
            "password2": "RondaSegura123",
        },
    )
    assert resp.status_code == 200  # re-renderiza con error
    assert User.objects.filter(email="dup@test.com").count() == 1


def test_login_with_email(client):
    User.objects.create_user(email="user@test.com", password="RondaSegura123")
    resp = client.post(
        reverse("accounts:login"),
        {"username": "user@test.com", "password": "RondaSegura123"},
    )
    assert resp.status_code == 302
    assert "_auth_user_id" in client.session


def test_dashboard_requires_login(client):
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_profile_requires_login(client):
    resp = client.get(reverse("accounts:profile"))
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_authenticated_user_sees_dashboard(client):
    User.objects.create_user(email="in@test.com", password="RondaSegura123")
    client.login(username="in@test.com", password="RondaSegura123")
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code == 200


def test_password_reset_sends_email(client):
    User.objects.create_user(email="reset@test.com", password="RondaSegura123")
    resp = client.post(reverse("accounts:password_reset"), {"email": "reset@test.com"})
    assert resp.status_code == 302
    assert len(mail.outbox) == 1
    assert "reset@test.com" in mail.outbox[0].to
