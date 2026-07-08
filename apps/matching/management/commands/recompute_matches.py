from django.core.management.base import BaseCommand

from apps.matching.services import recompute_all
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = "Recalcula los matches de compatibilidad entre empresas."

    def handle(self, *args, **options):
        total = 0
        for org in Organization.objects.all():
            n = recompute_all(org)
            total += n
            self.stdout.write(f"  {org.name}: {n} matches")
        self.stdout.write(self.style.SUCCESS(f"✓ {total} matches recalculados."))
