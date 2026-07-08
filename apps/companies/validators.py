"""Validación de CUIT (Clave Única de Identificación Tributaria, Argentina)."""

import re

from django.core.exceptions import ValidationError

_CUIT_WEIGHTS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def normalize_cuit(value: str) -> str:
    """Deja el CUIT sólo con dígitos (saca guiones y espacios)."""
    return re.sub(r"[\s-]", "", value or "")


def validate_cuit(value: str) -> None:
    """Valida formato (11 dígitos) y dígito verificador del CUIT."""
    digits = normalize_cuit(value)
    if not digits.isdigit() or len(digits) != 11:
        raise ValidationError("El CUIT debe tener 11 dígitos (ej: 30-71234567-8).")

    checksum = sum(int(d) * w for d, w in zip(digits[:10], _CUIT_WEIGHTS))
    verifier = 11 - (checksum % 11)
    if verifier == 11:
        verifier = 0
    elif verifier == 10:
        verifier = 9

    if verifier != int(digits[10]):
        raise ValidationError("El CUIT es inválido (dígito verificador incorrecto).")


def format_cuit(value: str) -> str:
    """Devuelve el CUIT formateado como XX-XXXXXXXX-X."""
    digits = normalize_cuit(value)
    if len(digits) != 11:
        return value
    return f"{digits[:2]}-{digits[2:10]}-{digits[10]}"
