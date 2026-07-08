from django.db import models


class Favorite(models.Model):
    """Una empresa guarda a otra como favorita."""

    owner = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="empresa que guarda",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="empresa guardada",
    )
    created_at = models.DateTimeField("guardado el", auto_now_add=True)

    class Meta:
        verbose_name = "favorito"
        verbose_name_plural = "favoritos"
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "company"], name="unique_favorite_owner_company"
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.owner} ★ {self.company}"


class ConnectionRequest(models.Model):
    """Solicitud de conexión/contacto entre empresas.

    Por ahora no comparte datos de contacto; sólo registra el vínculo comercial.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        ACCEPTED = "accepted", "Aceptada"
        REJECTED = "rejected", "Rechazada"

    from_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="sent_connections",
        verbose_name="empresa solicitante",
    )
    to_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="received_connections",
        verbose_name="empresa destinataria",
    )
    status = models.CharField(
        "estado", max_length=10, choices=Status.choices, default=Status.PENDING
    )
    message = models.CharField("mensaje", max_length=280, blank=True)
    created_at = models.DateTimeField("enviada el", auto_now_add=True)
    responded_at = models.DateTimeField("respondida el", null=True, blank=True)

    class Meta:
        verbose_name = "solicitud de conexión"
        verbose_name_plural = "solicitudes de conexión"
        constraints = [
            models.UniqueConstraint(
                fields=["from_company", "to_company"],
                name="unique_connection_from_to",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_company} → {self.to_company} ({self.get_status_display()})"
