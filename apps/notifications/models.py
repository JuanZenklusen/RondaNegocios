from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Alerta interna para un usuario (se muestra en la campanita)."""

    class Level(models.TextChoices):
        INFO = "info", "Información"
        SUCCESS = "success", "Éxito"
        WARNING = "warning", "Aviso"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="destinatario",
    )
    title = models.CharField("título", max_length=180)
    message = models.CharField("mensaje", max_length=300, blank=True)
    url = models.CharField("enlace", max_length=300, blank=True)
    level = models.CharField("nivel", max_length=10, choices=Level.choices, default=Level.INFO)
    is_read = models.BooleanField("leída", default=False)
    created_at = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient}: {self.title}"


class Message(models.Model):
    """Mensaje directo entre dos usuarios (mensajería interna)."""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="remitente",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="destinatario",
    )
    body = models.TextField("mensaje")
    created_at = models.DateTimeField("enviado el", auto_now_add=True)
    read_at = models.DateTimeField("leído el", null=True, blank=True)

    class Meta:
        verbose_name = "mensaje"
        verbose_name_plural = "mensajes"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} → {self.recipient}"
