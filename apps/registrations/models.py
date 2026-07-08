from django.conf import settings
from django.db import models


class Registration(models.Model):
    """Inscripción de un usuario (empresa o asistente) a un evento."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmada"
        REJECTED = "rejected", "Rechazada"
        CANCELLED = "cancelled", "Cancelada"

    class Payment(models.TextChoices):
        NOT_REQUIRED = "not_required", "Sin costo"
        SIMULATED = "simulated", "Pago simulado"
        PENDING = "pending", "Pago pendiente"

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="evento",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="usuario",
    )
    status = models.CharField(
        "estado", max_length=12, choices=Status.choices, default=Status.PENDING
    )
    payment_status = models.CharField(
        "pago", max_length=15, choices=Payment.choices, default=Payment.NOT_REQUIRED
    )
    amount = models.DecimalField("monto", max_digits=10, decimal_places=2, default=0)
    note = models.CharField("nota", max_length=280, blank=True)

    created_at = models.DateTimeField("inscripto el", auto_now_add=True)
    decided_at = models.DateTimeField("resuelto el", null=True, blank=True)

    class Meta:
        verbose_name = "inscripción"
        verbose_name_plural = "inscripciones"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"], name="unique_registration_event_user"
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.event} ({self.get_status_display()})"

    @property
    def is_active(self):
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)
