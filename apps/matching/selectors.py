"""Consultas de sugerencias/matches."""

from __future__ import annotations

from django.db.models import Q

from .models import Match


def top_matches_for(company, *, limit=5, min_score=1):
    """Devuelve las mejores empresas compatibles con `company`.

    Cada item: {"company": <Company>, "score": int, "details": dict}.
    """
    matches = (
        Match.objects.filter(Q(company_a=company) | Q(company_b=company))
        .filter(score__gte=min_score)
        .select_related("company_a", "company_b", "company_a__rubro", "company_b__rubro")
        .order_by("-score")[:limit]
    )
    result = []
    for m in matches:
        other = m.company_b if m.company_a_id == company.id else m.company_a
        result.append({"company": other, "score": m.score, "details": m.details})
    return result


def match_scores_map(company, other_ids):
    """Diccionario {company_id: score} de `company` contra un conjunto de ids."""
    matches = Match.objects.filter(
        (Q(company_a=company) & Q(company_b_id__in=other_ids))
        | (Q(company_b=company) & Q(company_a_id__in=other_ids))
    )
    scores = {}
    for m in matches:
        other_id = m.company_b_id if m.company_a_id == company.id else m.company_a_id
        scores[other_id] = m.score
    return scores
