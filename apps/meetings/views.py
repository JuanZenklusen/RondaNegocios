from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import CompanyRequiredMixin
from apps.companies.models import Company
from apps.companies.services import get_or_create_company_for_user
from apps.events.models import Event, TimeBlock
from apps.registrations.models import Registration

from . import selectors, services
from .models import Meeting, MeetingRequest
from .services import MeetingError


class _RoundAccessMixin(CompanyRequiredMixin):
    """Resuelve el evento y la empresa del usuario, y exige inscripción confirmada."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.event = get_object_or_404(Event, slug=kwargs.get("slug"))
        self.company = get_or_create_company_for_user(request.user)
        confirmed = Registration.objects.filter(
            event=self.event,
            user=request.user,
            status=Registration.Status.CONFIRMED,
        ).exists()
        if not confirmed:
            messages.error(
                request,
                "Necesitás tener tu inscripción confirmada para acceder a la ronda.",
            )
            return redirect(self.event.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)


class RoundView(_RoundAccessMixin, TemplateView):
    template_name = "meetings/round.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "rondas"
        ctx["event"] = self.event
        ctx["company"] = self.company
        ctx["agenda"] = selectors.company_agenda(self.event, self.company)
        ctx["received"] = selectors.received_pending_requests(self.event, self.company)
        ctx["sent"] = selectors.sent_requests(self.event, self.company)
        participants = list(selectors.participating_companies(self.event, exclude=self.company))
        # Ordena los participantes por compatibilidad (matching) desc.
        from apps.matching.selectors import match_scores_map

        scores = match_scores_map(self.company, [c.pk for c in participants])
        for c in participants:
            c.match_score = scores.get(c.pk, 0)
        participants.sort(key=lambda c: c.match_score, reverse=True)
        ctx["participants"] = participants
        ctx["time_blocks"] = self.event.time_blocks.all()
        return ctx


class RequestMeetingView(_RoundAccessMixin, View):
    def post(self, request, slug):
        to_company = get_object_or_404(Company, pk=request.POST.get("to_company"))
        time_block = get_object_or_404(
            TimeBlock, pk=request.POST.get("time_block"), event=self.event
        )
        try:
            services.request_meeting(
                event=self.event,
                from_company=self.company,
                to_company=to_company,
                time_block=time_block,
                message=request.POST.get("message", ""),
            )
            messages.success(request, "Solicitud de reunión enviada.")
        except MeetingError as exc:
            messages.error(request, str(exc))
        return redirect("meetings:round", slug=self.event.slug)


class RespondMeetingRequestView(CompanyRequiredMixin, View):
    def post(self, request, pk):
        company = get_or_create_company_for_user(request.user)
        meeting_request = get_object_or_404(MeetingRequest, pk=pk, to_company=company)
        action = request.POST.get("action")
        try:
            if action == "accept":
                services.accept_meeting_request(request=meeting_request)
                messages.success(request, "Reunión confirmada y mesa asignada.")
            else:
                services.reject_meeting_request(request=meeting_request)
                messages.success(request, "Solicitud rechazada.")
        except MeetingError as exc:
            messages.error(request, str(exc))
        return redirect("meetings:round", slug=meeting_request.event.slug)


class CancelMeetingView(CompanyRequiredMixin, View):
    def post(self, request, pk):
        company = get_or_create_company_for_user(request.user)
        meeting = get_object_or_404(
            Meeting.objects.filter(Q(company_a=company) | Q(company_b=company)),
            pk=pk,
        )
        services.cancel_meeting(meeting=meeting)
        messages.success(request, "Reunión cancelada.")
        return redirect("meetings:round", slug=meeting.event.slug)
