from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.accounts.mixins import CompanyRequiredMixin
from apps.companies.models import Company, Rubro
from apps.companies.services import get_or_create_company_for_user

from . import services
from .models import ConnectionRequest
from .selectors import search_companies


class _MyCompanyMixin(CompanyRequiredMixin):
    """Provee `self.my_company` (la empresa del usuario logueado)."""

    _my_company = None

    @property
    def my_company(self):
        if self._my_company is None:
            self._my_company = get_or_create_company_for_user(self.request.user)
        return self._my_company


class DirectoryView(_MyCompanyMixin, ListView):
    template_name = "networking/directory.html"
    context_object_name = "companies"
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        self.rubro_id = self.request.GET.get("rubro") or None
        self.province = self.request.GET.get("province", "").strip()
        return search_companies(
            user=self.request.user,
            query=self.query,
            rubro_id=self.rubro_id,
            province=self.province,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "red"
        ctx["rubros"] = Rubro.objects.all()
        ctx["provinces"] = (
            Company.objects.for_user(self.request.user)
            .exclude(province="")
            .values_list("province", flat=True)
            .distinct()
            .order_by("province")
        )
        ctx["q"] = self.query
        ctx["selected_rubro"] = self.rubro_id
        ctx["selected_province"] = self.province
        ctx["favorite_ids"] = set(self.my_company.favorites.values_list("company_id", flat=True))
        ctx["sent_connection_ids"] = set(
            self.my_company.sent_connections.values_list("to_company_id", flat=True)
        )
        # % de compatibilidad (matching) de cada empresa listada.
        from apps.matching.selectors import match_scores_map

        ctx["match_scores"] = match_scores_map(self.my_company, [c.pk for c in ctx["companies"]])
        return ctx


class FavoritesView(_MyCompanyMixin, ListView):
    template_name = "networking/favorites.html"
    context_object_name = "companies"
    paginate_by = 12

    def get_queryset(self):
        fav_ids = self.my_company.favorites.values_list("company_id", flat=True)
        return Company.objects.filter(pk__in=fav_ids).select_related("rubro")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "red"
        ctx["favorite_ids"] = set(self.object_list.values_list("pk", flat=True))
        ctx["sent_connection_ids"] = set(
            self.my_company.sent_connections.values_list("to_company_id", flat=True)
        )
        return ctx


class ConnectionsView(_MyCompanyMixin, TemplateView):
    template_name = "networking/connections.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_section"] = "red"
        ctx["received"] = self.my_company.received_connections.select_related(
            "from_company"
        ).filter(status=ConnectionRequest.Status.PENDING)
        ctx["sent"] = self.my_company.sent_connections.select_related("to_company")
        ctx["accepted"] = self.my_company.received_connections.select_related(
            "from_company"
        ).filter(status=ConnectionRequest.Status.ACCEPTED)
        return ctx


class ToggleFavoriteView(_MyCompanyMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(Company.objects.for_user(request.user), pk=pk)
        favorited = services.toggle_favorite(owner=self.my_company, target=target)
        return JsonResponse({"favorited": favorited})


class ConnectView(_MyCompanyMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(Company.objects.for_user(request.user), pk=pk)
        services.send_connection_request(from_company=self.my_company, to_company=target)
        return JsonResponse({"status": "pending"})


class RespondConnectionView(_MyCompanyMixin, View):
    def post(self, request, pk):
        connection = get_object_or_404(ConnectionRequest, pk=pk, to_company=self.my_company)
        accept = request.POST.get("action") == "accept"
        services.respond_connection_request(connection=connection, accept=accept)
        messages.success(request, "Conexión aceptada." if accept else "Solicitud rechazada.")
        return redirect("networking:connections")
