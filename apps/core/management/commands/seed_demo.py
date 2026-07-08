"""Puebla la base con datos de demostración: empresas completas, un organizador,
un asistente y un par de eventos con su programa.

Idempotente: se puede correr varias veces sin duplicar.
Al final escribe/actualiza CREDENCIALES-DEMO.txt (git-ignored) con los accesos.

Uso:  python manage.py seed_demo
"""

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.companies.models import Company, Need, Product, Rubro, Service
from apps.events.models import Activity, Event
from apps.organizations.services import get_default_organization

DEMO_PASSWORD = "Demo1234"

_CUIT_WEIGHTS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def build_cuit(ten_digits: str) -> str:
    """Construye un CUIT válido (con dígito verificador) desde 10 dígitos."""
    s = sum(int(d) * w for d, w in zip(ten_digits, _CUIT_WEIGHTS))
    v = 11 - (s % 11)
    v = 0 if v == 11 else (9 if v == 10 else v)
    return f"{ten_digits[:2]}-{ten_digits[2:10]}-{v}"


COMPANIES = [
    {
        "email": "agrotech@demo.com",
        "razon_social": "AgroTech del Litoral S.A.",
        "nombre_fantasia": "AgroTech",
        "cuit_base": "3071000010",
        "rubro": "tecnologia-y-software",
        "city": "Santa Fe",
        "province": "Santa Fe",
        "employees_count": 45,
        "website": "https://agrotech.example.com",
        "description": "Software de agricultura de precisión y sensores IoT para el campo.",
        "products": ["Plataforma de monitoreo de cultivos", "Sensores de humedad de suelo"],
        "services": ["Consultoría en digitalización agro", "Soporte y mantenimiento"],
        "needs": ["Distribuidores en la región NEA", "Proveedores de hardware IoT"],
    },
    {
        "email": "metalurgica@demo.com",
        "razon_social": "Metalúrgica Paraná S.R.L.",
        "nombre_fantasia": "MetalParaná",
        "cuit_base": "3071000029",
        "rubro": "metalurgica-y-metalmecanica",
        "city": "Paraná",
        "province": "Entre Ríos",
        "employees_count": 120,
        "website": "https://metalparana.example.com",
        "description": "Fabricación de piezas metalmecánicas y estructuras para la industria.",
        "products": ["Estructuras metálicas a medida", "Piezas torneadas CNC"],
        "services": ["Corte y plegado de chapa", "Soldadura industrial"],
        "needs": ["Proveedores de acero inoxidable", "Clientes del sector automotriz"],
    },
    {
        "email": "bioalimentos@demo.com",
        "razon_social": "BioAlimentos del Centro S.A.",
        "nombre_fantasia": "BioAlimentos",
        "cuit_base": "3071000037",
        "rubro": "alimentos-y-bebidas",
        "city": "Córdoba",
        "province": "Córdoba",
        "employees_count": 80,
        "website": "https://bioalimentos.example.com",
        "description": "Producción de alimentos orgánicos y saludables con certificación.",
        "products": ["Snacks orgánicos", "Harinas sin gluten"],
        "services": ["Marca blanca para retail"],
        "needs": ["Cadenas de supermercados", "Packaging sustentable"],
    },
    {
        "email": "logistica@demo.com",
        "razon_social": "Logística Andina S.A.",
        "nombre_fantasia": "Logística Andina",
        "cuit_base": "3071000045",
        "rubro": "transporte-y-logistica",
        "city": "Mendoza",
        "province": "Mendoza",
        "employees_count": 210,
        "website": "https://logandina.example.com",
        "description": "Transporte y almacenamiento con cobertura nacional y a Chile.",
        "products": [],
        "services": [
            "Transporte refrigerado",
            "Almacenamiento y distribución",
            "Logística de exportación",
        ],
        "needs": ["Software de ruteo en la nube", "Clientes exportadores"],
    },
    {
        "email": "textilsur@demo.com",
        "razon_social": "TextilSur S.R.L.",
        "nombre_fantasia": "TextilSur",
        "cuit_base": "3071000053",
        "rubro": "textil-e-indumentaria",
        "city": "La Plata",
        "province": "Buenos Aires",
        "employees_count": 60,
        "website": "https://textilsur.example.com",
        "description": "Confección de indumentaria de trabajo y uniformes corporativos.",
        "products": ["Uniformes corporativos", "Ropa de trabajo ignífuga"],
        "services": ["Bordado y estampado", "Diseño de indumentaria"],
        "needs": ["Proveedores de telas técnicas", "Licitaciones corporativas"],
    },
    {
        "email": "energiaverde@demo.com",
        "razon_social": "EnergíaVerde S.A.",
        "nombre_fantasia": "EnergíaVerde",
        "cuit_base": "3071000061",
        "rubro": "energia-y-renovables",
        "city": "Neuquén",
        "province": "Neuquén",
        "employees_count": 95,
        "website": "https://energiaverde.example.com",
        "description": "Soluciones de energía solar y eólica para industrias y municipios.",
        "products": ["Paneles solares", "Kits de autoconsumo"],
        "services": ["Instalación de parques solares", "Auditoría energética"],
        "needs": ["Financiamiento para proyectos", "Instaladores certificados"],
    },
]


class Command(BaseCommand):
    help = "Puebla la base con empresas, eventos y usuarios de demostración."

    def handle(self, *args, **options):
        org = get_default_organization()
        rubros = {r.slug: r for r in Rubro.objects.all()}
        created_lines = []

        # --- Empresas ---
        for data in COMPANIES:
            user, _ = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "role": User.Role.COMPANY,
                    "organization": org,
                    "first_name": data["nombre_fantasia"],
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.role = User.Role.COMPANY
            user.organization = org
            user.save()

            company, _ = Company.objects.get_or_create(
                user=user,
                defaults={"organization": org, "razon_social": data["razon_social"]},
            )
            company.organization = org
            company.razon_social = data["razon_social"]
            company.nombre_fantasia = data["nombre_fantasia"]
            company.cuit = build_cuit(data["cuit_base"])
            company.rubro = rubros.get(data["rubro"])
            company.city = data["city"]
            company.province = data["province"]
            company.country = "Argentina"
            company.employees_count = data["employees_count"]
            company.website = data["website"]
            company.description = data["description"]
            company.is_public = True
            company.save()

            company.products.all().delete()
            company.services.all().delete()
            company.needs.all().delete()
            for name in data["products"]:
                Product.objects.create(company=company, name=name)
            for name in data["services"]:
                Service.objects.create(company=company, name=name)
            for desc in data["needs"]:
                Need.objects.create(company=company, description=desc)

            created_lines.append(
                f"  Empresa   | {data['email']:24} | {DEMO_PASSWORD} | /empresa/{company.slug}/"
            )

        # --- Organizador ---
        organizer, _ = User.objects.get_or_create(
            email="organizador@demo.com",
            defaults={"role": User.Role.ORGANIZATION, "organization": org, "first_name": "Cámara"},
        )
        organizer.set_password(DEMO_PASSWORD)
        organizer.role = User.Role.ORGANIZATION
        organizer.organization = org
        organizer.save()
        created_lines.append(
            f"  Organizador | {'organizador@demo.com':22} | {DEMO_PASSWORD} | gestiona eventos"
        )

        # --- Asistente ---
        attendee, _ = User.objects.get_or_create(
            email="asistente@demo.com",
            defaults={"role": User.Role.ATTENDEE, "organization": org, "first_name": "Visitante"},
        )
        attendee.set_password(DEMO_PASSWORD)
        attendee.role = User.Role.ATTENDEE
        attendee.organization = org
        attendee.save()
        created_lines.append(
            f"  Asistente | {'asistente@demo.com':24} | {DEMO_PASSWORD} | público general"
        )

        # --- Eventos ---
        self._seed_events(org)

        # --- Archivo de credenciales ---
        self._write_credentials_file(created_lines)

        self.stdout.write(self.style.SUCCESS("\n✓ Datos de demostración cargados."))
        self.stdout.write("  Credenciales en: CREDENCIALES-DEMO.txt")

    def _seed_events(self, org):
        today = timezone.localdate()
        ronda, _ = Event.objects.get_or_create(
            slug="ronda-de-negocios-regional-2026",
            defaults={
                "organization": org,
                "name": "Ronda de Negocios Regional 2026",
                "event_type": Event.Type.BUSINESS_ROUND,
                "modality": Event.Modality.IN_PERSON,
                "status": Event.Status.PUBLISHED,
                "start_date": today + datetime.timedelta(days=20),
                "end_date": today + datetime.timedelta(days=21),
                "location": "Predio Ferial Provincial",
                "address": "Av. Siempreviva 1234",
                "description": "Dos jornadas de reuniones B2B, charlas y exposiciones.",
                "is_public": True,
                "general_price": 0,
                "meeting_duration_minutes": 30,
                "meetings_per_company": 12,
                "tables_count": 20,
            },
        )
        if not ronda.activities.exists():
            base = timezone.make_aware(
                datetime.datetime.combine(ronda.start_date, datetime.time(9, 0))
            )
            Activity.objects.create(
                event=ronda,
                title="Acreditación y bienvenida",
                activity_type=Activity.Type.OTHER,
                start=base,
                is_public=True,
                room="Hall central",
            )
            Activity.objects.create(
                event=ronda,
                title="Charla: Cómo exportar a Brasil",
                activity_type=Activity.Type.TALK,
                start=base + datetime.timedelta(hours=1),
                is_public=True,
                room="Auditorio A",
            )
            Activity.objects.create(
                event=ronda,
                title="Ronda de negocios (mesas)",
                activity_type=Activity.Type.BUSINESS_ROUND,
                start=base + datetime.timedelta(hours=2),
                is_public=False,
                room="Salón de mesas",
            )

        Event.objects.get_or_create(
            slug="expo-industrial-2026",
            defaults={
                "organization": org,
                "name": "Expo Industrial 2026",
                "event_type": Event.Type.FAIR,
                "modality": Event.Modality.IN_PERSON,
                "status": Event.Status.PUBLISHED,
                "start_date": today + datetime.timedelta(days=45),
                "end_date": today + datetime.timedelta(days=47),
                "location": "Centro de Convenciones",
                "description": "Feria abierta al público con stands, charlas y networking.",
                "is_public": True,
                "general_price": 2500,
            },
        )

    def _write_credentials_file(self, company_lines):
        path = settings.BASE_DIR / "CREDENCIALES-DEMO.txt"
        lines = [
            "CREDENCIALES DE DEMOSTRACIÓN — RondaNegocios",
            "=" * 60,
            "Generado por: python manage.py seed_demo",
            f"Contraseña para TODAS las cuentas: {DEMO_PASSWORD}",
            "El login es por EMAIL. Ingresá en /cuentas/ingresar/",
            "",
            "Rol         | Email                    | Contraseña | Nota",
            "-" * 60,
        ]
        lines.extend(company_lines)
        lines += [
            "",
            "Sugerencia de recorrido:",
            "  1. Entrá con una empresa y mirá su perfil (menú 'Perfil Empresa').",
            "  2. Abrí su perfil público (botón 'Ver perfil público').",
            "  3. Entrá a 'Red de Empresas': buscá, marcá favoritos y conectá.",
            "  4. Con 'organizador@demo.com' entrá a 'Gestión de eventos'.",
            "  5. Mirá los eventos públicos en /eventos/.",
            "",
            "NOTA: este archivo está en .gitignore (no se sube al repo).",
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
