from django.db import migrations

DEFAULT_SLUG = "principal"


def create_default_organization(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    Organization.objects.get_or_create(
        slug=DEFAULT_SLUG,
        defaults={
            "name": "Organización Principal",
            "description": "Organización por defecto del sistema.",
            "is_active": True,
        },
    )


def remove_default_organization(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    Organization.objects.filter(slug=DEFAULT_SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_organization, remove_default_organization),
    ]
