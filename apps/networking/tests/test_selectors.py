import pytest

from apps.companies.models import Rubro
from apps.networking.selectors import search_companies

pytestmark = pytest.mark.django_db


def test_directory_excludes_self_and_private(make_company):
    me = make_company(razon_social="Mi Empresa SA")
    other = make_company(razon_social="Otra SA", is_public=True)
    make_company(razon_social="Privada SA", is_public=False)

    result = search_companies(user=me.user)
    slugs = set(result.values_list("pk", flat=True))
    assert other.pk in slugs
    assert me.pk not in slugs  # no aparece uno mismo
    assert result.filter(is_public=False).count() == 0  # ni las privadas


def test_search_by_text(make_company):
    me = make_company(razon_social="Mi Empresa SA")
    make_company(razon_social="AgroIndustrias del Sur", description="soja y maíz")
    make_company(razon_social="TechCorp", description="software")

    result = search_companies(user=me.user, query="soja")
    names = list(result.values_list("razon_social", flat=True))
    assert names == ["AgroIndustrias del Sur"]


def test_filter_by_rubro(make_company):
    me = make_company(razon_social="Mi Empresa SA")
    tech = Rubro.objects.get(slug="tecnologia-y-software")
    make_company(razon_social="TechCorp", rubro=tech)
    make_company(razon_social="Otra SA")

    result = search_companies(user=me.user, rubro_id=tech.id)
    assert [c.razon_social for c in result] == ["TechCorp"]


def test_filter_by_province(make_company):
    me = make_company(razon_social="Mi Empresa SA")
    make_company(razon_social="Cordobesa SA", province="Córdoba")
    make_company(razon_social="Porteña SA", province="Buenos Aires")

    result = search_companies(user=me.user, province="Córdoba")
    assert [c.razon_social for c in result] == ["Cordobesa SA"]
