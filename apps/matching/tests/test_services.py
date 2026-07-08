import pytest

from apps.accounts.models import User
from apps.companies.models import Company, Need, Service
from apps.matching.models import Match
from apps.matching.selectors import match_scores_map, top_matches_for
from apps.matching.services import recompute_all, recompute_company_matches
from apps.organizations.services import get_default_organization

pytestmark = pytest.mark.django_db


def _company(email, razon_social):
    org = get_default_organization()
    user = User.objects.create_user(
        email=email, password="RondaSegura123", role=User.Role.COMPANY, organization=org
    )
    return Company.objects.create(user=user, organization=org, razon_social=razon_social)


def test_recompute_stores_single_row_per_pair():
    a = _company("a@t.com", "A")
    b = _company("b@t.com", "B")
    recompute_company_matches(a)
    recompute_company_matches(b)
    # Un solo Match por par, sin importar el orden.
    assert Match.objects.count() == 1
    m = Match.objects.first()
    assert m.company_a_id < m.company_b_id


def test_recompute_all_covers_all_pairs():
    _company("a@t.com", "A")
    _company("b@t.com", "B")
    _company("c@t.com", "C")
    org = get_default_organization()
    n = recompute_all(org)
    assert n == 3  # C(3,2) = 3 pares
    assert Match.objects.count() == 3


def test_top_matches_returns_counterpart_and_score():
    a = _company("a@t.com", "Soft")
    Service.objects.create(company=a, name="Software de ruteo")
    b = _company("b@t.com", "Logi")
    Need.objects.create(company=b, description="Software de ruteo")
    recompute_company_matches(a)

    top = top_matches_for(b, limit=5)
    assert len(top) == 1
    assert top[0]["company"].pk == a.pk
    assert top[0]["score"] > 0


def test_match_scores_map():
    a = _company("a@t.com", "A")
    b = _company("b@t.com", "B")
    recompute_company_matches(a)
    scores = match_scores_map(a, [b.pk])
    assert b.pk in scores
