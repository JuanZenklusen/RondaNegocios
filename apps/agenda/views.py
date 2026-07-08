from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.events.models import Activity, Event
from apps.registrations.models import Registration

from . import selectors, services
from .services import AgendaError


class _AgendaAccessMixin(LoginRequiredMixin):
    """Resuelve el evento y exige inscripción confirmada (empresa o asistente)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.event = get_object_or_404(Event, slug=kwargs.get("slug"))
        confirmed = Registration.objects.filter(
            event=self.event,
            user=request.user,
            status=Registration.Status.CONFIRMED,
        ).exists()
        if not confirmed:
            messages.error(request, "Necesitás tener tu inscripción confirmada al evento.")
            return redirect(self.event.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)


class MyEventAgendaView(_AgendaAccessMixin, TemplateView):
    template_name = "agenda/event_agenda.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "inscripciones"
        ctx["event"] = self.event
        ctx["program"] = selectors.program_by_day(self.event)
        ctx["attending_ids"] = selectors.attending_activity_ids(self.request.user, self.event)
        ctx["agenda"] = selectors.personal_agenda(self.request.user, self.event)
        ctx["is_company"] = self.request.user.is_company
        return ctx


class ToggleActivityAttendanceView(_AgendaAccessMixin, View):
    def post(self, request, slug, pk):
        activity = get_object_or_404(Activity, pk=pk, event=self.event)
        try:
            attending = services.toggle_activity_attendance(user=request.user, activity=activity)
            messages.success(
                request,
                "Agregado a tu agenda." if attending else "Quitado de tu agenda.",
            )
        except AgendaError as exc:
            messages.error(request, str(exc))
        url = reverse("agenda:event_agenda", kwargs={"slug": self.event.slug})
        return redirect(url + "#programa")
