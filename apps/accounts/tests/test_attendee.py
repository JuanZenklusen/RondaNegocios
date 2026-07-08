import pytest
from django.urls import reverse

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_attendee_registration_creates_attendee(client):
    resp = client.post(
        reverse("accounts:register_attendee"),
        {
            "email": "visitante@test.com",
            "first_name": "Vale",
            "password1": "RondaSegura123",
            "password2": "RondaSegura123",
        },
    )
    assert resp.status_code == 302
    user = User.objects.get(email="visitante@test.com")
    assert user.role == User.Role.ATTENDEE
    assert user.is_attendee is True
    assert user.organization is not None
    assert "_auth_user_id" in client.session
