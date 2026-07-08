from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.companies.services import get_or_create_company_for_user
from apps.matching.selectors import top_matches_for


class HomeView(TemplateView):
    """Landing pública."""

    template_name = "core/home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de la app (requiere login)."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "dashboard"
        if self.request.user.is_company:
            company = get_or_create_company_for_user(self.request.user)
            context["suggestions"] = top_matches_for(company, limit=4)
        return context
