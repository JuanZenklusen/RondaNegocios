"""Casos de uso de notificaciones y mensajería."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import Message, Notification


def notify(
    *, recipient, title, message="", url="", level=Notification.Level.INFO, email=False
) -> Notification:
    """Crea una notificación interna y, opcionalmente, envía un email."""
    notification = Notification.objects.create(
        recipient=recipient, title=title, message=message, url=url, level=level
    )
    if email and recipient.email:
        send_mail(
            subject=title,
            message=message or title,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@rondanegocios.local"),
            recipient_list=[recipient.email],
            fail_silently=True,
        )
    return notification


def mark_all_read(user) -> int:
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)


def mark_read(notification: Notification) -> Notification:
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    return notification


def send_message(*, sender, recipient, body: str) -> Message:
    """Envía un mensaje directo y notifica al destinatario."""
    message = Message.objects.create(sender=sender, recipient=recipient, body=body)
    sender_name = sender.get_full_name() or sender.email
    notify(
        recipient=recipient,
        title=f"Nuevo mensaje de {sender_name}",
        message=body[:120],
        url=reverse("notifications:conversation", args=[sender.pk]),
    )
    return message


def mark_conversation_read(*, user, other) -> int:
    return Message.objects.filter(recipient=user, sender=other, read_at__isnull=True).update(
        read_at=timezone.now()
    )
