import pytest

from apps.accounts.models import User
from apps.companies.models import Company, Need, Product, Rubro, Service
from apps.matching.scoring import compute_score
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


def _company(email, **kwargs):
    org = get_default_organization()
    user = User.objects.create_user(
        email=email, password="RondaSegura123", role=User.Role.COMPANY, organization=org
    )
    return Company.objects.create(user=user, organization=org, **kwargs)


def test_complementary_companies_score_high():
    a = _company("a@t.com", razon_social="Software SA")
    Service.objects.create(company=a, name="Software de ruteo en la nube")
    Need.objects.create(company=a, description="Clientes del sector logístico")

    b = _company("b@t.com", razon_social="Logística SA")
    Service.objects.create(company=b, name="Servicios de logística para clientes")
    Need.objects.create(company=b, description="Software de ruteo en la nube")

    score, details = compute_score(a, b)
    # A ofrece software que B busca, y B ofrece logística que A busca -> alto.
    assert details["coverage_ab"] == 1.0
    assert details["coverage_ba"] == 1.0
    assert score >= 70


def test_unrelated_companies_score_zero():
    a = _company("a@t.com", razon_social="Panadería SA")
    Product.objects.create(company=a, name="Pan artesanal")
    Need.objects.create(company=a, description="Harina de trigo")

    b = _company("b@t.com", razon_social="Software SA")
    Service.objects.create(company=b, name="Desarrollo de aplicaciones")
    Need.objects.create(company=b, description="Diseñadores UX")

    score, _ = compute_score(a, b)
    assert score == 0


def test_same_rubro_and_province_add_bonus():
    tech = Rubro.objects.get(slug="tecnologia-y-software")
    a = _company("a@t.com", razon_social="A SA", rubro=tech, province="Córdoba")
    b = _company("b@t.com", razon_social="B SA", rubro=tech, province="Córdoba")
    # Sin complementariedad, pero mismo rubro (0.15) + misma provincia (0.15).
    score, details = compute_score(a, b)
    assert details["rubro_match"] == 1.0
    assert details["province_match"] == 1.0
    assert score == 30  # round((0.15+0.15)*100)
