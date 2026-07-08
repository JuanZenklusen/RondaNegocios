"""Tests del aislamiento multi-tenant (OrganizationScopedQuerySet.for_user).

Se usa un modelo concreto de prueba (`managed=False`, así makemigrations lo
ignora) y se crea/borra su tabla con el schema_editor, para ejercitar el scoping
sin depender todavía de un modelo del dominio (Company llega en la Fase 3).
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import connection, models

from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationScopedModel

pytestmark = pytest.mark.django_db


class ScopedThing(OrganizationScopedModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "organizations"
        managed = False


@pytest.fixture
def scoped_table():
    # La tabla se crea dentro de la transacción del test; pytest-django hace
    # rollback al terminar, así que se elimina sola (no hace falta drop, que
    # además fallaría por triggers de FK pendientes dentro de la transacción).
    with connection.schema_editor() as editor:
        editor.create_model(ScopedThing)


def test_for_user_isolates_by_organization(scoped_table):
    org_a = Organization.objects.create(name="Org A", slug="org-a")
    org_b = Organization.objects.create(name="Org B", slug="org-b")
    ScopedThing.objects.create(name="a1", organization=org_a)
    ScopedThing.objects.create(name="b1", organization=org_b)

    user_a = User.objects.create_user(
        email="a@t.com",
        password="RondaSegura123",
        role=User.Role.COMPANY,
        organization=org_a,
    )
    superadmin = User.objects.create_superuser(email="s@t.com", password="x")
    user_sin_org = User.objects.create_user(
        email="n@t.com", password="RondaSegura123", role=User.Role.COMPANY
    )

    # Usuario de la org A: sólo ve lo de A.
    assert set(ScopedThing.objects.for_user(user_a).values_list("name", flat=True)) == {"a1"}
    # Superadmin: ve todo.
    assert ScopedThing.objects.for_user(superadmin).count() == 2
    # Usuario sin organización: no ve nada.
    assert ScopedThing.objects.for_user(user_sin_org).count() == 0
    # Anónimo: no ve nada.
    assert ScopedThing.objects.for_user(AnonymousUser()).count() == 0
