from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from apps.accounts.mixins import OrganizationRequiredMixin
from apps.events.models import Event

from . import services
from .models import Registration
from .services import RegistrationError

# ---------------------------------------------------------------------------
# Usuario que se inscribe (empresa / asistente)
# ---------------------------------------------------------------------------


class RegisterToEventView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, is_public=True)
        try:
            registration = services.register_user_to_event(user=request.user, event=event)
        except RegistrationError as exc:
            messages.error(request, str(exc))
            return redirect(event.get_absolute_url())

        if registration.status == Registration.Status.PENDING:
            messages.success(
                request,
                "¡Inscripción enviada! Queda pendiente de aprobación del organizador.",
            )
        else:
            messages.success(request, "¡Inscripción confirmada! Te esperamos en el evento.")
        return redirect("registrations:mine")


class MyRegistrationsView(LoginRequiredMixin, ListView):
    template_name = "registrations/my_registrations.html"
    context_object_name = "registrations"
    paginate_by = 20

    def get_queryset(self):
        return (
            Registration.objects.filter(user=self.request.user)
            .exclude(status=Registration.Status.CANCELLED)
            .select_related("event")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "inscripciones"
        return ctx


class CancelRegistrationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        registration = get_object_or_404(Registration, pk=pk, user=request.user)
        services.cancel_registration(registration=registration)
        messages.success(request, "Inscripción cancelada.")
        return redirect("registrations:mine")


# ---------------------------------------------------------------------------
# Organizador
# ---------------------------------------------------------------------------


class EventRegistrationsView(OrganizationRequiredMixin, ListView):
    template_name = "registrations/event_registrations.html"
    context_object_name = "registrations"

    def get_event(self):
        return get_object_or_404(Event.objects.for_user(self.request.user), pk=self.kwargs["pk"])

    def get_queryset(self):
        self.event = self.get_event()
        return self.event.registrations.select_related("user").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "eventos"
        ctx["event"] = self.event
        return ctx


class RespondRegistrationView(OrganizationRequiredMixin, View):
    def post(self, request, pk):
        registration = get_object_or_404(
            Registration.objects.select_related("event"),
            pk=pk,
            event__in=Event.objects.for_user(request.user),
        )
        approve = request.POST.get("action") == "approve"
        services.decide_registration(registration=registration, approve=approve)
        messages.success(request, "Inscripción aprobada." if approve else "Inscripción rechazada.")
        return redirect("registrations:event_registrations", pk=registration.event_id)
