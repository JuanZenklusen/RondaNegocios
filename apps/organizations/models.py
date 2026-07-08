from django.db import models


class Organization(models.Model):
    """Entidad que organiza eventos (cámara, municipio, universidad, etc.).

    Es la raíz del aislamiento multi-tenant: todo dato del dominio cuelga de una
    organización. Por ahora habrá una sola, pero la estructura queda lista para
    escalar a varias con independencia de datos.
    """

    name = models.CharField("nombre", max_length=200)
    slug = models.SlugField("identificador", unique=True)
    description = models.TextField("descripción", blank=True)
    logo = models.ImageField("logo", upload_to="organizations/logos/", blank=True, null=True)
    email = models.EmailField("email de contacto", blank=True)
    phone = models.CharField("teléfono", max_length=50, blank=True)
    website = models.URLField("sitio web", blank=True)
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "organización"
        verbose_name_plural = "organizaciones"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationScopedQuerySet(models.QuerySet):
    """QuerySet que sabe filtrar por la organización del usuario."""

    def for_user(self, user):
        """Devuelve sólo los objetos visibles para `user`.

        - Superadmin: ve todo.
        - Usuario con organización: ve sólo la suya.
        - Usuario sin organización (o anónimo): no ve nada.
        """
        if not user or not user.is_authenticated:
            return self.none()
        if user.is_superuser or user.role == "superadmin":
            return self
        if getattr(user, "organization_id", None):
            return self.filter(organization_id=user.organization_id)
        return self.none()


class OrganizationScopedModel(models.Model):
    """Base abstracta para todo modelo del dominio que pertenece a una
    organización. Los modelos concretos (Company, Event, etc.) la heredan.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="organización",
    )

    objects = OrganizationScopedQuerySet.as_manager()

    class Meta:
        abstract = True
