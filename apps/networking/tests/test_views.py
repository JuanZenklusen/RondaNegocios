import pytest
from django.urls import reverse

from apps.networking.models import ConnectionRequest, Favorite

pytestmark = pytest.mark.django_db


def test_directory_requires_login(client):
    resp = client.get(reverse("networking:directory"))
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_directory_renders(client, make_company):
    me = make_company(razon_social="Mi Empresa SA")
    make_company(razon_social="Visible SA", is_public=True)
    client.force_login(me.user)
    resp = client.get(reverse("networking:directory"))
    assert resp.status_code == 200
    assert b"Visible SA" in resp.content


def test_toggle_favorite_endpoint(client, make_company):
    me = make_company(razon_social="Mi Empresa SA")
    target = make_company(razon_social="Target SA")
    client.force_login(me.user)

    resp = client.post(reverse("networking:toggle_favorite", args=[target.pk]))
    assert resp.status_code == 200
    assert resp.json()["favorited"] is True
    assert Favorite.objects.filter(owner=me, company=target).exists()

    # Segundo toggle lo quita.
    resp = client.post(reverse("networking:toggle_favorite", args=[target.pk]))
    assert resp.json()["favorited"] is False


def test_connect_endpoint_creates_request(client, make_company):
    me = make_company(razon_social="Mi Empresa SA")
    target = make_company(razon_social="Target SA")
    client.force_login(me.user)

    resp = client.post(reverse("networking:connect", args=[target.pk]))
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"
    assert ConnectionRequest.objects.filter(from_company=me, to_company=target).exists()


def test_respond_connection_accept(client, make_company):
    me = make_company(razon_social="Mi Empresa SA")
    other = make_company(razon_social="Other SA")
    conn = ConnectionRequest.objects.create(from_company=other, to_company=me)
    client.force_login(me.user)

    resp = client.post(
        reverse("networking:respond_connection", args=[conn.pk]), {"action": "accept"}
    )
    assert resp.status_code == 302
    conn.refresh_from_db()
    assert conn.status == ConnectionRequest.Status.ACCEPTED


def test_cannot_respond_others_connection(client, make_company):
    me = make_company(razon_social="Mi Empresa SA")
    a = make_company(razon_social="A SA")
    b = make_company(razon_social="B SA")
    conn = ConnectionRequest.objects.create(from_company=a, to_company=b)
    client.force_login(me.user)

    resp = client.post(
        reverse("networking:respond_connection", args=[conn.pk]), {"action": "accept"}
    )
    assert resp.status_code == 404  # no es la destinataria
