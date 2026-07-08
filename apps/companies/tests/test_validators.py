import pytest
from django.core.exceptions import ValidationError

from apps.companies.validators import format_cuit, normalize_cuit, validate_cuit

VALID_CUIT = "30-71234567-1"  # dígito verificador correcto = 1


def test_valid_cuit_passes():
    validate_cuit(VALID_CUIT)


def test_invalid_check_digit_fails():
    with pytest.raises(ValidationError):
        validate_cuit("30-71234567-4")


def test_wrong_length_fails():
    with pytest.raises(ValidationError):
        validate_cuit("123")


def test_normalize_and_format():
    assert normalize_cuit(VALID_CUIT) == "30712345671"
    assert format_cuit("30712345671") == VALID_CUIT
