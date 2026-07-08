"""Lecturas de mensajería (inbox y conversaciones)."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Message

User = get_user_model()


def conversation_messages(user, other):
    return Message.objects.filter(
        Q(sender=user, recipient=other) | Q(sender=other, recipient=user)
    ).select_related("sender", "recipient")


def inbox(user):
    """Lista de conversaciones: por cada interlocutor, el último mensaje y no leídos."""
    messages = (
        Message.objects.filter(Q(sender=user) | Q(recipient=user))
        .select_related("sender", "recipient")
        .order_by("-created_at")
    )
    conversations: dict[int, dict] = {}
    for m in messages:
        other = m.recipient if m.sender_id == user.id else m.sender
        conv = conversations.setdefault(other.id, {"other": other, "last": m, "unread": 0})
        if m.recipient_id == user.id and m.read_at is None:
            conv["unread"] += 1
    return list(conversations.values())
