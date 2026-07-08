import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory
from django.views.generic import View

from apps.accounts.mixins import CompanyRequiredMixin
from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class _DummyCompanyView(CompanyRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("ok")


def test_company_role_allowed():
    user = User.objects.create_user(
        email="c@test.com", password="RondaSegura123", role=User.Role.COMPANY
    )
    request = RequestFactory().get("/")
    request.user = user
    resp = _DummyCompanyView.as_view()(request)
    assert resp.status_code == 200


def test_other_role_denied():
    user = User.objects.create_user(
        email="o@test.com", password="RondaSegura123", role=User.Role.ORGANIZATION
    )
    request = RequestFactory().get("/")
    request.user = user
    with pytest.raises(PermissionDenied):
        _DummyCompanyView.as_view()(request)
