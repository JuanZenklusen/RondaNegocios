from django.db import migrations
from django.utils.text import slugify

RUBROS = [
    "Agroindustria",
    "Alimentos y Bebidas",
    "Automotriz y Autopartes",
    "Comercio y Distribución",
    "Construcción",
    "Educación y Capacitación",
    "Energía y Renovables",
    "Metalúrgica y Metalmecánica",
    "Química y Plásticos",
    "Salud y Farmacéutica",
    "Servicios Profesionales",
    "Tecnología y Software",
    "Textil e Indumentaria",
    "Transporte y Logística",
    "Turismo y Hotelería",
]


def seed_rubros(apps, schema_editor):
    Rubro = apps.get_model("companies", "Rubro")
    for name in RUBROS:
        Rubro.objects.get_or_create(slug=slugify(name), defaults={"name": name})


def unseed_rubros(apps, schema_editor):
    Rubro = apps.get_model("companies", "Rubro")
    Rubro.objects.filter(slug__in=[slugify(n) for n in RUBROS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_rubros, unseed_rubros),
    ]
