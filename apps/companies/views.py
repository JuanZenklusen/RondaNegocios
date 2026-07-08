from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from apps.accounts.mixins import CompanyRequiredMixin

from . import services
from .forms import CompanyForm, NeedFormSet, ProductFormSet, ServiceFormSet
from .models import Company


class CompanyProfileEditView(CompanyRequiredMixin, View):
    """Edición del perfil de la empresa del usuario (datos +
    productos/servicios/necesidades vía formsets)."""

    template_name = "companies/profile_form.html"

    def get_company(self):
        return services.get_or_create_company_for_user(self.request.user)

    def _context(self, form, product_fs, service_fs, need_fs):
        return {
            "form": form,
            "product_formset": product_fs,
            "service_formset": service_fs,
            "need_formset": need_fs,
            "active_section": "empresa",
        }

    def get(self, request, *args, **kwargs):
        company = self.get_company()
        ctx = self._context(
            CompanyForm(instance=company),
            ProductFormSet(instance=company, prefix="products"),
            ServiceFormSet(instance=company, prefix="services"),
            NeedFormSet(instance=company, prefix="needs"),
        )
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        company = self.get_company()
        form = CompanyForm(request.POST, request.FILES, instance=company)
        product_fs = ProductFormSet(request.POST, instance=company, prefix="products")
        service_fs = ServiceFormSet(request.POST, instance=company, prefix="services")
        need_fs = NeedFormSet(request.POST, instance=company, prefix="needs")

        if all(
            [
                form.is_valid(),
                product_fs.is_valid(),
                service_fs.is_valid(),
                need_fs.is_valid(),
            ]
        ):
            form.save()
            product_fs.save()
            service_fs.save()
            need_fs.save()
            messages.success(request, "Perfil de empresa actualizado correctamente.")
            return redirect("companies:profile_edit")

        messages.error(request, "Revisá los campos: hay errores en el formulario.")
        ctx = self._context(form, product_fs, service_fs, need_fs)
        return render(request, self.template_name, ctx)


class CompanyPublicDetailView(DetailView):
    """Perfil público de la empresa (sin login, SEO-friendly)."""

    model = Company
    template_name = "companies/public_detail.html"
    context_object_name = "company"

    def get_queryset(self):
        return Company.objects.filter(is_public=True).select_related("rubro")
