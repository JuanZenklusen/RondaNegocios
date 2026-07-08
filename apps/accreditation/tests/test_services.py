import pytest

from apps.accreditation.models import Participant
from apps.accreditation.services import (
    AccreditationError,
    accredit_participant,
    check_in,
    check_out,
    get_or_create_self_accreditation,
)

from .conftest import confirm

pytestmark = pytest.mark.django_db


def test_self_accreditation_is_unique(attendee_user, event):
    reg = confirm(event, attendee_user)
    a1 = get_or_create_self_accreditation(reg)
    a2 = get_or_create_self_accreditation(reg)
    assert a1.pk == a2.pk
    assert a1.participant is None
    assert a1.code  # tiene código para el QR


def test_holder_name_for_participant(company_user, event):
    reg = confirm(event, company_user)
    p = Participant.objects.create(
        company=company_user.company, first_name="Ana", last_name="Pérez", cargo="CEO"
    )
    acc = accredit_participant(registration=reg, participant=p)
    assert acc.holder_name == "Ana Pérez"
    assert acc.holder_company == company_user.company


def test_cannot_accredit_foreign_participant(company_user, attendee_user, event, org):
    from apps.companies.models import Company

    reg = confirm(event, company_user)
    other_user = attendee_user
    other_company = Company.objects.create(
        user=other_user, organization=org, razon_social="Otra SA"
    )
    foreign = Participant.objects.create(company=other_company, first_name="X", last_name="Y")
    with pytest.raises(AccreditationError):
        accredit_participant(registration=reg, participant=foreign)


def test_check_in_then_out(attendee_user, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    assert acc.status == "pending"
    check_in(acc)
    assert acc.status == "checked_in"
    check_out(acc)
    assert acc.status == "checked_out"


def test_cannot_check_out_without_check_in(attendee_user, event):
    reg = confirm(event, attendee_user)
    acc = get_or_create_self_accreditation(reg)
    with pytest.raises(AccreditationError):
        check_out(acc)
