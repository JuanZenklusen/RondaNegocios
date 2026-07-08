from django.db import models


class MeetingRequest(models.Model):
    """Solicitud de reunión de una empresa a otra dentro de una ronda.

    Mientras está pendiente, reserva tentativamente el bloque en la agenda de
    ambas. Al aceptarse se crea una `Meeting` confirmada con mesa asignada.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        ACCEPTED = "accepted", "Aceptada"
        REJECTED = "rejected", "Rechazada"
        CANCELLED = "cancelled", "Cancelada"

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="meeting_requests",
        verbose_name="evento",
    )
    from_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="sent_meeting_requests",
        verbose_name="empresa solicitante",
    )
    to_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="received_meeting_requests",
        verbose_name="empresa destinataria",
    )
    time_block = models.ForeignKey(
        "events.TimeBlock",
        on_delete=models.CASCADE,
        related_name="meeting_requests",
        verbose_name="bloque horario propuesto",
    )
    status = models.CharField(
        "estado", max_length=10, choices=Status.choices, default=Status.PENDING
    )
    message = models.CharField("mensaje", max_length=280, blank=True)
    created_at = models.DateTimeField("solicitada el", auto_now_add=True)
    responded_at = models.DateTimeField("respondida el", null=True, blank=True)

    class Meta:
        verbose_name = "solicitud de reunión"
        verbose_name_plural = "solicitudes de reunión"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["from_company", "to_company", "time_block"],
                name="unique_meeting_request",
            ),
        ]

    def __str__(self):
        return f"{self.from_company} → {self.to_company} ({self.get_status_display()})"


class Meeting(models.Model):
    """Reunión confirmada entre dos empresas, con mesa y bloque horario."""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmada"
        CANCELLED = "cancelled", "Cancelada"

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="meetings",
        verbose_name="evento",
    )
    request = models.OneToOneField(
        MeetingRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meeting",
        verbose_name="solicitud",
    )
    company_a = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="meetings_as_a",
        verbose_name="empresa A",
    )
    company_b = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="meetings_as_b",
        verbose_name="empresa B",
    )
    time_block = models.ForeignKey(
        "events.TimeBlock",
        on_delete=models.CASCADE,
        related_name="meetings",
        verbose_name="bloque horario",
    )
    table = models.ForeignKey(
        "events.Table",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meetings",
        verbose_name="mesa",
    )
    status = models.CharField(
        "estado", max_length=10, choices=Status.choices, default=Status.CONFIRMED
    )
    created_at = models.DateTimeField("creada el", auto_now_add=True)

    class Meta:
        verbose_name = "reunión"
        verbose_name_plural = "reuniones"
        ordering = ["time_block__date", "time_block__start_time"]

    def __str__(self):
        return f"{self.company_a} × {self.company_b}"

    def other_company(self, company):
        """Devuelve la contraparte de `company` en esta reunión."""
        return self.company_b if self.company_a_id == company.id else self.company_a
