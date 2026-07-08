"""Provee a todos los templates los contadores de la campanita y mensajes."""

from .models import Message, Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "nav_recent_notifications": list(Notification.objects.filter(recipient=request.user)[:6]),
        "nav_unread_notifications": Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
        "nav_unread_messages": Message.objects.filter(
            recipient=request.user, read_at__isnull=True
        ).count(),
    }
