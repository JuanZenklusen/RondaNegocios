"""Recalculo y persistencia de matches."""

from __future__ import annotations

from django.db import transaction

from apps.companies.models import Company

from .models import Match
from .scoring import compute_score


def _ordered(company_a, company_b):
    """Devuelve el par ordenado por id (para no duplicar registros)."""
    return (company_a, company_b) if company_a.pk < company_b.pk else (company_b, company_a)


@transaction.atomic
def upsert_match(company_a, company_b) -> Match:
    a, b = _ordered(company_a, company_b)
    score, details = compute_score(a, b)
    match, _ = Match.objects.update_or_create(
        company_a=a,
        company_b=b,
        defaults={"organization": a.organization, "score": score, "details": details},
    )
    return match


def recompute_company_matches(company: Company) -> int:
    """Recalcula los matches de `company` contra el resto de su organización."""
    others = Company.objects.filter(organization=company.organization).exclude(pk=company.pk)
    count = 0
    for other in others:
        upsert_match(company, other)
        count += 1
    return count


def recompute_all(organization) -> int:
    """Recalcula todos los pares de la organización. Devuelve cuántos matches."""
    companies = list(Company.objects.filter(organization=organization))
    count = 0
    for i, a in enumerate(companies):
        for b in companies[i + 1 :]:
            upsert_match(a, b)
            count += 1
    return count
