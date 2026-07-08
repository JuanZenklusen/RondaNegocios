"""Mixins para vistas que trabajan con datos scopeados por organización."""


class OrganizationScopedQuerysetMixin:
    """Filtra el queryset de la vista a la organización del usuario.

    Requiere que el modelo use `OrganizationScopedQuerySet` (o un manager con
    método `for_user`). Combinar con `LoginRequiredMixin`.
    """

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class OrganizationFormMixin:
    """Asigna automáticamente la organización del usuario al crear objetos
    scopeados, para que las vistas no tengan que hacerlo a mano."""

    def form_valid(self, form):
        if not form.instance.organization_id:
            form.instance.organization = self.request.user.organization
        return super().form_valid(form)
