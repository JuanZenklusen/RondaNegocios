import pytest

from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


def test_default_organization_is_seeded():
    """La data migration crea la organización principal."""
    assert Organization.objects.filter(slug="principal").exists()


def test_organization_str():
    org = Organization.objects.create(name="Cámara Industrial", slug="camara-industrial")
    assert str(org) == "Cámara Industrial"


def test_user_can_belong_to_organization():
    from apps.accounts.models import User

    org = Organization.objects.create(name="Muni", slug="muni")
    user = User.objects.create_user(email="u@muni.com", password="RondaSegura123", organization=org)
    assert user.organization == org
    assert user in org.users.all()
