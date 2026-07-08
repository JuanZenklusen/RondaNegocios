"""Consultas de lectura del directorio de empresas."""

from __future__ import annotations

from django.db.models import Q

from apps.companies.models import Company


def search_companies(*, user, query="", rubro_id=None, province=""):
    """Directorio de empresas visibles para `user`, con búsqueda y filtros.

    - Scopeado a la organización del usuario (multi-tenant).
    - Sólo perfiles públicos.
    - Excluye la propia empresa del usuario.
    """
    qs = Company.objects.for_user(user).filter(is_public=True).select_related("rubro")

    company = Company.objects.filter(user=user).first()
    if company:
        qs = qs.exclude(pk=company.pk)

    if query:
        qs = qs.filter(
            Q(razon_social__icontains=query)
            | Q(nombre_fantasia__icontains=query)
            | Q(description__icontains=query)
            | Q(products__name__icontains=query)
            | Q(services__name__icontains=query)
        ).distinct()

    if rubro_id:
        qs = qs.filter(rubro_id=rubro_id)

    if province:
        qs = qs.filter(province__iexact=province)

    return qs
