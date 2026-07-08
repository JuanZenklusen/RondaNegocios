import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def company_user():
    return User.objects.create_user(
        email="empresa@test.com",
        password="RondaSegura123",
        role=User.Role.COMPANY,
        organization=get_default_organization(),
    )


def _login(client, user):
    client.force_login(user)


def test_profile_edit_requires_login(client):
    resp = client.get(reverse("companies:profile_edit"))
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_profile_edit_creates_company_on_first_visit(client, company_user):
    _login(client, company_user)
    assert not Company.objects.filter(user=company_user).exists()
    resp = client.get(reverse("companies:profile_edit"))
    assert resp.status_code == 200
    assert Company.objects.filter(user=company_user).exists()


def test_profile_edit_saves_data_and_formsets(client, company_user):
    _login(client, company_user)
    client.get(reverse("companies:profile_edit"))  # crea la company
    data = {
        "razon_social": "TechSolutions SRL",
        "nombre_fantasia": "TechSolutions",
        "cuit": "30-71234567-1",
        "country": "Argentina",
        # management forms de los 3 formsets
        "products-TOTAL_FORMS": "1",
        "products-INITIAL_FORMS": "0",
        "products-MIN_NUM_FORMS": "0",
        "products-MAX_NUM_FORMS": "1000",
        "products-0-name": "Software a medida",
        "products-0-description": "Desarrollo",
        "services-TOTAL_FORMS": "0",
        "services-INITIAL_FORMS": "0",
        "services-MIN_NUM_FORMS": "0",
        "services-MAX_NUM_FORMS": "1000",
        "needs-TOTAL_FORMS": "1",
        "needs-INITIAL_FORMS": "0",
        "needs-MIN_NUM_FORMS": "0",
        "needs-MAX_NUM_FORMS": "1000",
        "needs-0-description": "Proveedores de hardware",
    }
    resp = client.post(reverse("companies:profile_edit"), data)
    assert resp.status_code == 302
    company = Company.objects.get(user=company_user)
    assert company.razon_social == "TechSolutions SRL"
    assert company.cuit == "30-71234567-1"
    assert company.products.count() == 1
    assert company.needs.count() == 1


def test_profile_edit_rejects_invalid_cuit(client, company_user):
    _login(client, company_user)
    client.get(reverse("companies:profile_edit"))
    data = {
        "razon_social": "X SA",
        "cuit": "30-71234567-9",  # verificador incorrecto
        "products-TOTAL_FORMS": "0",
        "products-INITIAL_FORMS": "0",
        "products-MIN_NUM_FORMS": "0",
        "products-MAX_NUM_FORMS": "1000",
        "services-TOTAL_FORMS": "0",
        "services-INITIAL_FORMS": "0",
        "services-MIN_NUM_FORMS": "0",
        "services-MAX_NUM_FORMS": "1000",
        "needs-TOTAL_FORMS": "0",
        "needs-INITIAL_FORMS": "0",
        "needs-MIN_NUM_FORMS": "0",
        "needs-MAX_NUM_FORMS": "1000",
    }
    resp = client.post(reverse("companies:profile_edit"), data)
    assert resp.status_code == 200  # re-renderiza con error
    assert b"CUIT" in resp.content


def test_public_profile_visible_when_public(client, company_user):
    company = Company.objects.create(
        user=company_user,
        organization=company_user.organization,
        razon_social="Pública SA",
        is_public=True,
    )
    resp = client.get(company.get_absolute_url())
    assert resp.status_code == 200
    assert b"P\xc3\xbablica SA" in resp.content


def test_public_profile_hidden_when_private(client, company_user):
    company = Company.objects.create(
        user=company_user,
        organization=company_user.organization,
        razon_social="Privada SA",
        is_public=False,
    )
    resp = client.get(company.get_absolute_url())
    assert resp.status_code == 404
