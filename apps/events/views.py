from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.accounts.mixins import OrganizationRequiredMixin
from apps.organizations.mixins import (
    OrganizationFormMixin,
    OrganizationScopedQuerysetMixin,
)

from . import services
from .forms import ActivityFormSet, EventForm
from .models import Event

# ---------------------------------------------------------------------------
# Gestión (organizador)
# ---------------------------------------------------------------------------


class OrganizerEventListView(OrganizationRequiredMixin, OrganizationScopedQuerysetMixin, ListView):
    model = Event
    template_name = "events/organizer_list.html"
    context_object_name = "events"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "eventos"
        return ctx


class _EventFormMixin(OrganizationRequiredMixin):
    """Maneja el formset de actividades junto al form del evento."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "eventos"
        if self.request.POST:
            ctx["activity_formset"] = ActivityFormSet(
                self.request.POST, instance=self.object, prefix="activities"
            )
        else:
            ctx["activity_formset"] = ActivityFormSet(instance=self.object, prefix="activities")
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)  # guarda el evento -> self.object
        formset = ActivityFormSet(self.request.POST, instance=self.object, prefix="activities")
        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Evento guardado correctamente.")
            return response
        messages.error(self.request, "Revisá las actividades: hay errores.")
        return self.render_to_response(self.get_context_data(form=form))


class OrganizerEventCreateView(_EventFormMixin, OrganizationFormMixin, CreateView):
    def get_success_url(self):
        return reverse_lazy("events:update", kwargs={"pk": self.object.pk})


class OrganizerEventUpdateView(_EventFormMixin, OrganizationScopedQuerysetMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy("events:update", kwargs={"pk": self.object.pk})


class OrganizerEventDeleteView(
    OrganizationRequiredMixin, OrganizationScopedQuerysetMixin, DeleteView
):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        messages.success(self.request, "Evento eliminado.")
        return super().form_valid(form)


class GenerateScheduleView(OrganizationRequiredMixin, View):
    """Genera las mesas y bloques horarios de la ronda de un evento."""

    def post(self, request, pk):
        event = get_object_or_404(Event.objects.for_user(request.user), pk=pk)
        if not (event.round_start_time and event.round_end_time):
            messages.error(
                request,
                "Definí la hora de inicio y fin de la ronda antes de generar el cronograma.",
            )
            return redirect("events:update", pk=event.pk)
        result = services.generate_event_schedule(event)
        messages.success(
            request,
            f"Cronograma generado: {result['tables_created']} mesas y "
            f"{result['blocks_created']} bloques horarios nuevos.",
        )
        return redirect("events:update", pk=event.pk)


# ---------------------------------------------------------------------------
# Público
# ---------------------------------------------------------------------------


class PublicEventListView(ListView):
    template_name = "events/public_list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        return Event.objects.filter(
            status=Event.Status.PUBLISHED,
            is_public=True,
            end_date__gte=timezone.localdate(),
        ).order_by("start_date")


class PublicEventDetailView(DetailView):
    template_name = "events/public_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(is_public=True).exclude(status=Event.Status.DRAFT)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["activities"] = self.object.activities.all()
        if self.request.user.is_authenticated:
            ctx["my_registration"] = self.object.registrations.filter(
                user=self.request.user
            ).first()
        return ctx
