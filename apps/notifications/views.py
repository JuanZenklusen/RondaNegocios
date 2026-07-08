from django.contrib import messages as flash
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from . import selectors, services
from .models import Notification

User = get_user_model()


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "notificaciones"
        return ctx


class OpenNotificationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        services.mark_read(notification)
        return redirect(notification.url or "notifications:list")


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        services.mark_all_read(request.user)
        flash.success(request, "Notificaciones marcadas como leídas.")
        return redirect("notifications:list")


# --- Mensajería ---


class InboxView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/inbox.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "mensajes"
        ctx["conversations"] = selectors.inbox(self.request.user)
        return ctx


class ConversationView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/conversation.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        other = get_object_or_404(User, pk=kwargs["user_pk"])
        services.mark_conversation_read(user=self.request.user, other=other)
        ctx["other"] = other
        ctx["messages_list"] = selectors.conversation_messages(self.request.user, other)
        ctx["active_section"] = "mensajes"
        return ctx


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, user_pk):
        other = get_object_or_404(User, pk=user_pk)
        body = (request.POST.get("body") or "").strip()
        if other.pk == request.user.pk:
            flash.error(request, "No podés enviarte un mensaje a vos mismo.")
        elif body:
            services.send_message(sender=request.user, recipient=other, body=body)
        return redirect("notifications:conversation", user_pk=other.pk)
