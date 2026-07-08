from django.conf import settings
from django.db import models


class ActivityAttendance(models.Model):
    """Marca que un usuario asistirá a una actividad del programa de un evento.

    Con estas marcas se autocompleta la agenda personal del inscripto.
    """

    activity = models.ForeignKey(
        "events.Activity",
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="actividad",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_attendances",
        verbose_name="usuario",
    )
    created_at = models.DateTimeField("agregado el", auto_now_add=True)

    class Meta:
        verbose_name = "asistencia a actividad"
        verbose_name_plural = "asistencias a actividades"
        constraints = [
            models.UniqueConstraint(fields=["activity", "user"], name="unique_activity_attendance"),
        ]

    def __str__(self):
        return f"{self.user} → {self.activity}"
