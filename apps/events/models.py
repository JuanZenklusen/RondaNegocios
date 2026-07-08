from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.organizations.models import OrganizationScopedModel


def _unique_event_slug(base, instance_pk=None):
    base = slugify(base) or "evento"
    slug = base
    i = 2
    qs = Event.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


class Event(OrganizationScopedModel):
    """Evento organizado (ronda de negocios, feria, congreso, etc.).

    Un evento puede tener un programa con varias actividades (charlas,
    exposiciones, reuniones públicas, la ronda de negocios en sí).
    """

    class Type(models.TextChoices):
        BUSINESS_ROUND = "business_round", "Ronda de negocios"
        FAIR = "fair", "Feria"
        EXHIBITION = "exhibition", "Exposición"
        CONGRESS = "congress", "Congreso"
        TRAINING = "training", "Capacitación"
        SEMINAR = "seminar", "Seminario"
        WORKSHOP = "workshop", "Workshop"
        MEETING = "meeting", "Encuentro empresarial"

    class Modality(models.TextChoices):
        IN_PERSON = "in_person", "Presencial"
        VIRTUAL = "virtual", "Virtual"
        HYBRID = "hybrid", "Híbrido"

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"
        FINISHED = "finished", "Finalizado"
        CANCELLED = "cancelled", "Cancelado"

    name = models.CharField("nombre", max_length=200)
    slug = models.SlugField("identificador público", max_length=220, unique=True, blank=True)
    description = models.TextField("descripción", blank=True)
    event_type = models.CharField(
        "tipo", max_length=20, choices=Type.choices, default=Type.BUSINESS_ROUND
    )
    modality = models.CharField(
        "modalidad", max_length=15, choices=Modality.choices, default=Modality.IN_PERSON
    )
    status = models.CharField("estado", max_length=12, choices=Status.choices, default=Status.DRAFT)

    start_date = models.DateField("fecha de inicio")
    end_date = models.DateField("fecha de fin")

    location = models.CharField("lugar / sede", max_length=200, blank=True)
    address = models.CharField("dirección", max_length=255, blank=True)
    cover = models.ImageField(
        "imagen de portada", upload_to="events/covers/", blank=True, null=True
    )

    capacity = models.PositiveIntegerField("cupo total", null=True, blank=True)
    # Entrada general para el público (simulada por ahora; pagos = fase posterior).
    general_price = models.DecimalField(
        "precio entrada general", max_digits=10, decimal_places=2, default=0
    )

    is_public = models.BooleanField("visible al público", default=True)

    # Configuración de la ronda de negocios
    meeting_duration_minutes = models.PositiveIntegerField(
        "duración de cada reunión (min)", default=30
    )
    meetings_per_company = models.PositiveIntegerField(
        "reuniones por empresa", null=True, blank=True
    )
    tables_count = models.PositiveIntegerField("cantidad de mesas", default=0)

    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        verbose_name = "evento"
        verbose_name_plural = "eventos"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_event_slug(self.name, self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:public_detail", kwargs={"slug": self.slug})

    @property
    def is_upcoming(self):
        return self.end_date >= timezone.localdate()

    @property
    def is_free(self):
        return self.general_price == 0


class Activity(models.Model):
    """Actividad del programa de un evento (charla, exposición, reunión pública…)."""

    class Type(models.TextChoices):
        TALK = "talk", "Charla"
        EXHIBITION = "exhibition", "Exposición"
        PUBLIC_MEETING = "public_meeting", "Reunión pública"
        BUSINESS_ROUND = "business_round", "Ronda de negocios"
        WORKSHOP = "workshop", "Workshop"
        OTHER = "other", "Otra"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="evento",
    )
    title = models.CharField("título", max_length=200)
    description = models.TextField("descripción", blank=True)
    activity_type = models.CharField("tipo", max_length=20, choices=Type.choices, default=Type.TALK)
    start = models.DateTimeField("inicio")
    end = models.DateTimeField("fin", null=True, blank=True)
    room = models.CharField("sala / espacio", max_length=120, blank=True)
    capacity = models.PositiveIntegerField("cupo", null=True, blank=True)
    is_public = models.BooleanField("abierta al público general", default=True)

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["start"]

    def __str__(self):
        return self.title


class Table(models.Model):
    """Mesa física donde se realizan las reuniones de la ronda de negocios."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="tables", verbose_name="evento"
    )
    number = models.PositiveIntegerField("número")

    class Meta:
        verbose_name = "mesa"
        verbose_name_plural = "mesas"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["event", "number"], name="unique_table_per_event"),
        ]

    def __str__(self):
        return f"Mesa {self.number}"


class TimeBlock(models.Model):
    """Bloque horario de la ronda (slot de reunión)."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="time_blocks",
        verbose_name="evento",
    )
    date = models.DateField("fecha")
    start_time = models.TimeField("hora de inicio")
    end_time = models.TimeField("hora de fin")

    class Meta:
        verbose_name = "bloque horario"
        verbose_name_plural = "bloques horarios"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.date} {self.start_time:%H:%M}–{self.end_time:%H:%M}"
