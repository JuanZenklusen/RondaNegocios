"""Mixins de control de acceso por rol para vistas basadas en clases."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import User


class RoleRequiredMixin(LoginRequiredMixin):
    """Exige que el usuario esté autenticado y tenga uno de los roles permitidos.

    Uso:
        class MiVista(RoleRequiredMixin, View):
            allowed_roles = [User.Role.ORGANIZATION, User.Role.SUPERADMIN]
    """

    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("No tenés permisos para acceder a esta sección.")
        return super().dispatch(request, *args, **kwargs)


class CompanyRequiredMixin(RoleRequiredMixin):
    allowed_roles = [User.Role.COMPANY]


class OrganizationRequiredMixin(RoleRequiredMixin):
    allowed_roles = [User.Role.ORGANIZATION, User.Role.SUPERADMIN]
