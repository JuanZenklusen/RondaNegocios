from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from . import services
from .forms import (
    AttendeeRegistrationForm,
    CompanyRegistrationForm,
    EmailAuthenticationForm,
    ProfileForm,
)


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = CompanyRegistrationForm
    success_url = reverse_lazy("core:dashboard")

    def form_valid(self, form):
        user = services.register_company_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
        )
        login(self.request, user)
        messages.success(self.request, "¡Cuenta creada! Bienvenido a RondaNegocios.")
        return super().form_valid(form)


class AttendeeRegisterView(FormView):
    template_name = "accounts/register_attendee.html"
    form_class = AttendeeRegistrationForm
    success_url = reverse_lazy("events:public_list")

    def form_valid(self, form):
        user = services.register_attendee_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
        )
        login(self.request, user)
        messages.success(
            self.request, "¡Cuenta de asistente creada! Ya podés inscribirte a eventos."
        )
        return super().form_valid(form)


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "ajustes"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)
