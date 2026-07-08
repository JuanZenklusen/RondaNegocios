import qrcode
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import CompanyRequiredMixin, OrganizationRequiredMixin
from apps.companies.services import get_or_create_company_for_user
from apps.events.models import Event
from apps.registrations.models import Registration

from . import services
from .forms import ParticipantForm
from .models import Accreditation, Participant
from .services import AccreditationError


def _can_see(user, accreditation) -> bool:
    return user.is_authenticated and (
        user == accreditation.registration.user or user.is_organization or user.is_superuser
    )


# ---------------------------------------------------------------------------
# QR (imagen PNG)
# ---------------------------------------------------------------------------


class QRView(LoginRequiredMixin, View):
    def get(self, request, code):
        accreditation = get_object_or_404(Accreditation, code=code)
        if not _can_see(request.user, accreditation):
            raise Http404
        url = request.build_absolute_uri(reverse("accreditation:checkin", args=[code]))
        img = qrcode.make(url, box_size=8, border=2)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response


# ---------------------------------------------------------------------------
# Titular (empresa / asistente)
# ---------------------------------------------------------------------------


class CredentialsView(LoginRequiredMixin, TemplateView):
    template_name = "accreditation/credentials.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "credenciales"
        user = self.request.user
        regs = (
            Registration.objects.filter(user=user, status=Registration.Status.CONFIRMED)
            .select_related("event")
            .order_by("event__start_date")
        )
        for reg in regs:
            services.get_or_create_self_accreditation(reg)

        ctx["registrations"] = [
            {
                "registration": reg,
                "accreditations": reg.accreditations.select_related("participant").all(),
            }
            for reg in regs
        ]
        if user.is_company:
            company = get_or_create_company_for_user(user)
            ctx["is_company"] = True
            ctx["participants"] = company.participants.all()
            ctx["participant_form"] = ParticipantForm()
        return ctx


class CredentialDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accreditation/credential_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        accreditation = get_object_or_404(Accreditation, code=kwargs["code"])
        if not _can_see(self.request.user, accreditation):
            raise Http404
        ctx["accreditation"] = accreditation
        ctx["active_section"] = "credenciales"
        return ctx


class ParticipantCreateView(CompanyRequiredMixin, View):
    def post(self, request):
        company = get_or_create_company_for_user(request.user)
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.company = company
            participant.save()
            messages.success(request, "Representante agregado.")
        else:
            messages.error(request, "Revisá los datos del representante.")
        return redirect("accreditation:credentials")


class ParticipantDeleteView(CompanyRequiredMixin, View):
    def post(self, request, pk):
        company = get_or_create_company_for_user(request.user)
        participant = get_object_or_404(Participant, pk=pk, company=company)
        participant.delete()
        messages.success(request, "Representante eliminado.")
        return redirect("accreditation:credentials")


class AccreditParticipantView(CompanyRequiredMixin, View):
    def post(self, request, registration_pk):
        registration = get_object_or_404(Registration, pk=registration_pk, user=request.user)
        company = get_or_create_company_for_user(request.user)
        participant = get_object_or_404(
            Participant, pk=request.POST.get("participant"), company=company
        )
        try:
            services.accredit_participant(registration=registration, participant=participant)
            messages.success(request, "Credencial generada para el representante.")
        except AccreditationError as exc:
            messages.error(request, str(exc))
        return redirect("accreditation:credentials")


# ---------------------------------------------------------------------------
# Organizador: check-in / control de asistencia
# ---------------------------------------------------------------------------


class CheckInView(OrganizationRequiredMixin, View):
    """Destino del QR: el organizador registra ingreso/egreso."""

    template_name = "accreditation/checkin.html"

    def get_accreditation(self, request, code):
        return get_object_or_404(
            Accreditation.objects.select_related("registration__event"),
            code=code,
            registration__event__in=Event.objects.for_user(request.user),
        )

    def get(self, request, code):
        accreditation = self.get_accreditation(request, code)
        return render(request, self.template_name, {"accreditation": accreditation})

    def post(self, request, code):
        accreditation = self.get_accreditation(request, code)
        action = request.POST.get("action")
        try:
            if action == "checkout":
                services.check_out(accreditation)
                messages.success(request, "Egreso registrado.")
            else:
                services.check_in(accreditation)
                messages.success(request, "Ingreso registrado.")
        except AccreditationError as exc:
            messages.error(request, str(exc))
        return redirect("accreditation:checkin", code=code)


class EventAccreditationsView(OrganizationRequiredMixin, TemplateView):
    template_name = "accreditation/event_accreditations.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        event = get_object_or_404(Event.objects.for_user(self.request.user), pk=kwargs["pk"])
        ctx["event"] = event
        ctx["active_section"] = "eventos"
        ctx["accreditations"] = (
            Accreditation.objects.filter(registration__event=event)
            .select_related("registration__user", "participant")
            .order_by("checked_in_at")
        )
        return ctx
