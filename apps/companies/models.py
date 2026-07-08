from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.organizations.models import OrganizationScopedModel

from .validators import validate_cuit


class Rubro(models.Model):
    """Catálogo global de rubros/sectores de actividad."""

    name = models.CharField("nombre", max_length=120, unique=True)
    slug = models.SlugField("identificador", max_length=140, unique=True)

    class Meta:
        verbose_name = "rubro"
        verbose_name_plural = "rubros"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def _unique_slug(model, base, instance_pk=None):
    """Genera un slug único para `model` a partir de `base`."""
    base = slugify(base) or "empresa"
    slug = base
    i = 2
    qs = model.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


class Company(OrganizationScopedModel):
    """Perfil institucional de una empresa (estilo LinkedIn)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name="usuario",
    )

    # Identidad
    razon_social = models.CharField("razón social", max_length=200)
    nombre_fantasia = models.CharField("nombre de fantasía", max_length=200, blank=True)
    cuit = models.CharField(
        "CUIT",
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_cuit],
    )
    slug = models.SlugField("identificador público", max_length=220, unique=True, blank=True)
    description = models.TextField("descripción", blank=True)
    rubro = models.ForeignKey(
        Rubro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
        verbose_name="rubro",
    )
    logo = models.ImageField("logo", upload_to="companies/logos/", blank=True, null=True)

    # Contacto y redes
    website = models.URLField("sitio web", blank=True)
    email = models.EmailField("email de contacto", blank=True)
    phone = models.CharField("teléfono", max_length=50, blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    facebook = models.URLField("Facebook", blank=True)

    # Ubicación
    address = models.CharField("dirección", max_length=255, blank=True)
    city = models.CharField("localidad", max_length=120, blank=True)
    province = models.CharField("provincia", max_length=120, blank=True)
    country = models.CharField("país", max_length=120, blank=True, default="Argentina")

    # Datos productivos
    employees_count = models.PositiveIntegerField("cantidad de empleados", null=True, blank=True)
    production_capacity = models.TextField("capacidad productiva", blank=True)
    certifications = models.TextField("certificaciones", blank=True)

    is_public = models.BooleanField("perfil público", default=True)
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.nombre_fantasia or self.razon_social
            self.slug = _unique_slug(Company, base, self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("companies:public_detail", kwargs={"slug": self.slug})

    @property
    def display_name(self):
        return self.nombre_fantasia or self.razon_social


class Product(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="empresa",
    )
    name = models.CharField("nombre", max_length=200)
    description = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="empresa",
    )
    name = models.CharField("nombre", max_length=200)
    description = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Need(models.Model):
    """Necesidad declarada por la empresa (lo que busca). Clave para el matching."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="needs",
        verbose_name="empresa",
    )
    description = models.CharField("necesidad", max_length=300)

    class Meta:
        verbose_name = "necesidad"
        verbose_name_plural = "necesidades"
        ordering = ["description"]

    def __str__(self):
        return self.description
