import uuid

from django.db import models


def _generate_code():
    return uuid.uuid4().hex


class Participant(models.Model):
    """Representante de una empresa que asiste a los eventos."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="empresa",
    )
    first_name = models.CharField("nombre", max_length=120)
    last_name = models.CharField("apellido", max_length=120)
    cargo = models.CharField("cargo", max_length=120, blank=True)
    email = models.EmailField("email", blank=True)
    phone = models.CharField("teléfono", max_length=50, blank=True)
    created_at = models.DateTimeField("creado", auto_now_add=True)

    class Meta:
        verbose_name = "representante"
        verbose_name_plural = "representantes"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Accreditation(models.Model):
    """Credencial de acceso a un evento, con QR y control de asistencia.

    Puede pertenecer a un representante de empresa (participant) o al propio
    inscripto (asistente), en cuyo caso `participant` es nulo.
    """

    registration = models.ForeignKey(
        "registrations.Registration",
        on_delete=models.CASCADE,
        related_name="accreditations",
        verbose_name="inscripción",
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="accreditations",
        verbose_name="representante",
    )
    code = models.CharField("código", max_length=32, unique=True, default=_generate_code)
    checked_in_at = models.DateTimeField("ingreso", null=True, blank=True)
    checked_out_at = models.DateTimeField("egreso", null=True, blank=True)
    created_at = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "acreditación"
        verbose_name_plural = "acreditaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.holder_name} @ {self.event}"

    @property
    def event(self):
        return self.registration.event

    @property
    def holder_name(self):
        if self.participant:
            return self.participant.full_name
        user = self.registration.user
        return user.get_full_name() or user.email

    @property
    def holder_company(self):
        if self.participant:
            return self.participant.company
        return getattr(self.registration.user, "company", None)

    @property
    def status(self):
        if self.checked_out_at:
            return "checked_out"
        if self.checked_in_at:
            return "checked_in"
        return "pending"
