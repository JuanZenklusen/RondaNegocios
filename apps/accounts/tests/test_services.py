import pytest
from django.contrib.auth import authenticate

from apps.accounts.models import User
from apps.accounts.services import register_company_user

pytestmark = pytest.mark.django_db


def test_register_company_user_creates_company_role():
    user = register_company_user(
        email="empresa@test.com",
        password="RondaSegura123",
        first_name="Ana",
        last_name="Pérez",
    )
    assert user.pk is not None
    assert user.email == "empresa@test.com"
    assert user.role == User.Role.COMPANY
    assert user.is_company is True
    assert user.is_staff is False


def test_register_company_user_hashes_password_and_authenticates():
    register_company_user(email="login@test.com", password="RondaSegura123")
    # La contraseña queda hasheada, no en texto plano.
    user = User.objects.get(email="login@test.com")
    assert user.password != "RondaSegura123"
    # Y sirve para autenticar (email como USERNAME_FIELD).
    assert authenticate(username="login@test.com", password="RondaSegura123") is not None


def test_register_company_user_assigns_default_organization():
    user = register_company_user(email="org@test.com", password="RondaSegura123")
    assert user.organization is not None
    assert user.organization.slug == "principal"


def test_create_superuser_gets_superadmin_role():
    admin = User.objects.create_superuser(email="admin@test.com", password="x")
    assert admin.is_superuser is True
    assert admin.is_staff is True
    assert admin.role == User.Role.SUPERADMIN
