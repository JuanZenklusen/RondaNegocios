from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Landing pública."""

    template_name = "core/home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de la app (requiere login)."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "dashboard"
        return context
