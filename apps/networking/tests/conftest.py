import pytest

from apps.accounts.models import User
from apps.companies.models import Company
from apps.organizations.services import get_default_organization


@pytest.fixture
def make_company(db):
    """Fábrica de (usuario empresa + perfil Company) en la organización por defecto."""
    counter = {"n": 0}

    def _make(razon_social="Empresa SA", **company_kwargs):
        counter["n"] += 1
        org = get_default_organization()
        user = User.objects.create_user(
            email=f"c{counter['n']}@test.com",
            password="RondaSegura123",
            role=User.Role.COMPANY,
            organization=org,
        )
        company = Company.objects.create(
            user=user, organization=org, razon_social=razon_social, **company_kwargs
        )
        return company

    return _make
