import pytest

from apps.networking.models import ConnectionRequest, Favorite
from apps.networking.services import (
    respond_connection_request,
    send_connection_request,
    toggle_favorite,
)

pytestmark = pytest.mark.django_db


def test_toggle_favorite_adds_then_removes(make_company):
    a = make_company(razon_social="A SA")
    b = make_company(razon_social="B SA")

    assert toggle_favorite(owner=a, target=b) is True
    assert Favorite.objects.filter(owner=a, company=b).exists()

    assert toggle_favorite(owner=a, target=b) is False
    assert not Favorite.objects.filter(owner=a, company=b).exists()


def test_cannot_favorite_self(make_company):
    a = make_company(razon_social="A SA")
    with pytest.raises(ValueError):
        toggle_favorite(owner=a, target=a)


def test_send_connection_is_idempotent(make_company):
    a = make_company(razon_social="A SA")
    b = make_company(razon_social="B SA")

    c1 = send_connection_request(from_company=a, to_company=b)
    c2 = send_connection_request(from_company=a, to_company=b)
    assert c1.pk == c2.pk
    assert ConnectionRequest.objects.filter(from_company=a, to_company=b).count() == 1


def test_respond_connection_accept(make_company):
    a = make_company(razon_social="A SA")
    b = make_company(razon_social="B SA")
    conn = send_connection_request(from_company=a, to_company=b)

    respond_connection_request(connection=conn, accept=True)
    conn.refresh_from_db()
    assert conn.status == ConnectionRequest.Status.ACCEPTED
    assert conn.responded_at is not None
