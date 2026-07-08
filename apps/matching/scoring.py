"""Algoritmo de compatibilidad entre empresas.

Idea: dos empresas machean cuando lo que una **ofrece** (productos/servicios)
responde a lo que la otra **busca** (necesidades). Se pondera principalmente esa
complementariedad, con bonus menores por rubro y ubicación compartidos.
"""

from __future__ import annotations

import re

# Peso de cada componente (suman 1.0).
W_COMPLEMENTARITY = 0.70
W_RUBRO = 0.15
W_PROVINCE = 0.15

_STOPWORDS = {
    "de",
    "la",
    "el",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    "para",
    "por",
    "con",
    "sin",
    "del",
    "al",
    "en",
    "y",
    "o",
    "u",
    "que",
    "los",
    "las",
    "su",
    "sus",
    "lo",
    "les",
    "nos",
    "se",
    "a",
    "e",
}

_TOKEN_RE = re.compile(r"[a-záéíóúñü0-9]+")


def _tokens(text: str) -> set[str]:
    if not text:
        return set()
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) >= 3 and t not in _STOPWORDS}


def _offer_bag(company) -> set[str]:
    """Conjunto de palabras clave de lo que la empresa ofrece."""
    bag: set[str] = set()
    for product in company.products.all():
        bag |= _tokens(product.name) | _tokens(product.description)
    for service in company.services.all():
        bag |= _tokens(service.name) | _tokens(service.description)
    bag |= _tokens(company.description)
    return bag


def _need_token_sets(company) -> list[set[str]]:
    """Una bolsa de palabras por cada necesidad declarada."""
    return [_tokens(need.description) for need in company.needs.all()]


def _coverage(offer_bag: set[str], needs: list[set[str]]) -> float:
    """Fracción de necesidades cubiertas por la oferta (0..1)."""
    if not needs:
        return 0.0
    matched = sum(1 for need in needs if need & offer_bag)
    return matched / len(needs)


def compute_score(company_a, company_b) -> tuple[int, dict]:
    """Devuelve (score 0-100, desglose) de compatibilidad entre dos empresas."""
    offer_a = _offer_bag(company_a)
    offer_b = _offer_bag(company_b)
    needs_a = _need_token_sets(company_a)
    needs_b = _need_token_sets(company_b)

    cov_ab = _coverage(offer_a, needs_b)  # A cubre lo que B busca
    cov_ba = _coverage(offer_b, needs_a)  # B cubre lo que A busca
    complementarity = (cov_ab + cov_ba) / 2

    rubro_match = 1.0 if company_a.rubro_id and company_a.rubro_id == company_b.rubro_id else 0.0
    province_match = (
        1.0
        if company_a.province and company_a.province.lower() == company_b.province.lower()
        else 0.0
    )

    score01 = (
        W_COMPLEMENTARITY * complementarity + W_RUBRO * rubro_match + W_PROVINCE * province_match
    )
    score = round(score01 * 100)

    details = {
        "complementarity": round(complementarity, 3),
        "coverage_ab": round(cov_ab, 3),
        "coverage_ba": round(cov_ba, 3),
        "rubro_match": rubro_match,
        "province_match": province_match,
    }
    return score, details
