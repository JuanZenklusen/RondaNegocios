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
        "address": "Parque Tecnológico Litoral, Ruta 168 km 0",
        "employees_count": 45,
        "website": "https://agrotech.example.com",
        "contact_email": "contacto@agrotech.example.com",
        "phone": "+54 342 400-1010",
        "linkedin": "https://linkedin.com/company/agrotech-litoral",
        "instagram": "https://instagram.com/agrotech.litoral",
        "facebook": "",
        "production_capacity": "Fábrica de sensores con capacidad de 5.000 unidades/mes.",
        "certifications": "ISO 9001:2015 · Certificación INTA de compatibilidad agro.",
        "description": "Software de agricultura de precisión y sensores IoT para el campo.",
        "products": [
            (
                "Plataforma de monitoreo de cultivos",
                "Software en la nube con mapas y alertas en tiempo real.",
            ),
            (
                "Sensores de humedad de suelo",
                "Dispositivos IoT de bajo consumo con conectividad LoRa.",
            ),
        ],
        "services": [
            (
                "Consultoría en digitalización agro",
                "Diagnóstico y hoja de ruta de transformación digital.",
            ),
            ("Soporte y mantenimiento", "Soporte técnico y actualizaciones del sistema."),
        ],
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
        "address": "Parque Industrial Paraná, Calle 3 Nº 450",
        "employees_count": 120,
        "website": "https://metalparana.example.com",
        "contact_email": "ventas@metalparana.example.com",
        "phone": "+54 343 421-2020",
        "linkedin": "https://linkedin.com/company/metalparana",
        "instagram": "",
        "facebook": "https://facebook.com/metalparana",
        "production_capacity": "Planta de 8.000 m² con 3 líneas de producción CNC.",
        "certifications": "ISO 9001:2015 · Normas IRAM de soldadura.",
        "description": "Fabricación de piezas metalmecánicas y estructuras para la industria.",
        "products": [
            ("Estructuras metálicas a medida", "Naves industriales, depósitos y galpones."),
            ("Piezas torneadas CNC", "Mecanizado de precisión en acero y aluminio."),
        ],
        "services": [
            ("Corte y plegado de chapa", "Corte láser y plegado hasta 6 mm."),
            ("Soldadura industrial", "Soldadura MIG/TIG certificada."),
        ],
        "needs": [
            "Proveedores de acero inoxidable",
            "Logística de exportación de piezas",
        ],
    },
    {
        "email": "bioalimentos@demo.com",
        "razon_social": "BioAlimentos del Centro S.A.",
        "nombre_fantasia": "BioAlimentos",
        "cuit_base": "3071000037",
        "rubro": "alimentos-y-bebidas",
        "city": "Córdoba",
        "province": "Córdoba",
        "address": "Av. de los Alimentos 1200, Córdoba",
        "employees_count": 80,
        "website": "https://bioalimentos.example.com",
        "contact_email": "hola@bioalimentos.example.com",
        "phone": "+54 351 455-3030",
        "linkedin": "https://linkedin.com/company/bioalimentos-centro",
        "instagram": "https://instagram.com/bioalimentos",
        "facebook": "",
        "production_capacity": "Planta habilitada SENASA, 2.000 kg/día de productos secos.",
        "certifications": "Certificación Orgánica Argentina · HACCP.",
        "description": "Producción de alimentos orgánicos y saludables con certificación.",
        "products": [
            ("Snacks orgánicos", "Línea de snacks saludables sin conservantes."),
            ("Harinas sin gluten", "Harinas de arroz, garbanzo y almendra."),
        ],
        "services": [
            ("Marca blanca para retail", "Producción de línea propia para supermercados."),
        ],
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
        "address": "Acceso Este 3400, Guaymallén, Mendoza",
        "employees_count": 210,
        "website": "https://logandina.example.com",
        "contact_email": "operaciones@logandina.example.com",
        "phone": "+54 261 430-4040",
        "linkedin": "https://linkedin.com/company/logistica-andina",
        "instagram": "",
        "facebook": "https://facebook.com/logisticaandina",
        "production_capacity": "Flota de 80 camiones y 12.000 m² de depósito.",
        "certifications": "ISO 39001 (seguridad vial) · Operador logístico habilitado.",
        "description": "Transporte y almacenamiento con cobertura nacional y a Chile.",
        "products": [
            ("Cámaras de frío", "Espacios refrigerados para cadena de frío."),
        ],
        "services": [
            ("Transporte refrigerado", "Cadena de frío para alimentos y farma."),
            ("Almacenamiento y distribución", "Depósito y última milla a todo el país."),
            (
                "Logística de exportación de piezas y maquinaria",
                "Gestión aduanera y transporte a Chile.",
            ),
        ],
        "needs": [
            "Software de ruteo en la nube",
            "Estructuras metálicas para depósitos",
        ],
    },
    {
        "email": "textilsur@demo.com",
        "razon_social": "TextilSur S.R.L.",
        "nombre_fantasia": "TextilSur",
        "cuit_base": "3071000053",
        "rubro": "textil-e-indumentaria",
        "city": "La Plata",
        "province": "Buenos Aires",
        "address": "Calle 44 Nº 780, La Plata",
        "employees_count": 60,
        "website": "https://textilsur.example.com",
        "contact_email": "ventas@textilsur.example.com",
        "phone": "+54 221 489-5050",
        "linkedin": "https://linkedin.com/company/textilsur",
        "instagram": "https://instagram.com/textilsur",
        "facebook": "",
        "production_capacity": "Taller con 40 máquinas y 15.000 prendas/mes.",
        "certifications": "Certificación de ropa ignífuga IRAM.",
        "description": "Confección de indumentaria de trabajo y uniformes corporativos.",
        "products": [
            ("Uniformes corporativos", "Diseño y confección a medida para empresas."),
            ("Ropa de trabajo ignífuga", "Indumentaria de seguridad certificada."),
        ],
        "services": [
            ("Bordado y estampado", "Personalización con logo de la empresa."),
            ("Diseño de indumentaria", "Desarrollo de líneas de indumentaria laboral."),
        ],
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
        "address": "Parque Industrial Neuquén, Lote 22",
        "employees_count": 95,
        "website": "https://energiaverde.example.com",
        "contact_email": "info@energiaverde.example.com",
        "phone": "+54 299 442-6060",
        "linkedin": "https://linkedin.com/company/energiaverde",
        "instagram": "https://instagram.com/energiaverde",
        "facebook": "",
        "production_capacity": "Capacidad de instalación de 5 MW anuales.",
        "certifications": "Instalador certificado por la Secretaría de Energía.",
        "description": "Soluciones de energía solar y eólica para industrias y municipios.",
        "products": [
            ("Paneles solares", "Módulos fotovoltaicos de alta eficiencia."),
            ("Kits de autoconsumo", "Kits llave en mano para pymes y hogares."),
        ],
        "services": [
            ("Instalación de parques solares", "Proyecto y montaje de parques solares."),
            ("Auditoría energética", "Diagnóstico de eficiencia y ahorro."),
        ],
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
            company.description = data["description"]
            # Contacto y redes
            company.email = data["contact_email"]
            company.phone = data["phone"]
            company.website = data["website"]
            company.linkedin = data["linkedin"]
            company.instagram = data["instagram"]
            company.facebook = data["facebook"]
            # Ubicación
            company.address = data["address"]
            company.city = data["city"]
            company.province = data["province"]
            company.country = "Argentina"
            # Datos productivos
            company.employees_count = data["employees_count"]
            company.production_capacity = data["production_capacity"]
            company.certifications = data["certifications"]
            company.is_public = True
            company.save()

            company.products.all().delete()
            company.services.all().delete()
            company.needs.all().delete()
            for name, desc in data["products"]:
                Product.objects.create(company=company, name=name, description=desc)
            for name, desc in data["services"]:
                Service.objects.create(company=company, name=name, description=desc)
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

        # --- Matching (compatibilidad entre empresas) ---
        from apps.matching.services import recompute_all

        recompute_all(org)

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
        # Programa de 2 días (se recrea en cada corrida).
        ronda.activities.all().delete()

        def _at(day_offset, hour, minute=0):
            day = ronda.start_date + datetime.timedelta(days=day_offset)
            return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour, minute)))

        # Día 1
        Activity.objects.create(
            event=ronda,
            title="Acreditación y bienvenida",
            activity_type=Activity.Type.OTHER,
            start=_at(0, 9),
            end=_at(0, 9, 30),
            is_public=True,
            room="Hall central",
        )
        Activity.objects.create(
            event=ronda,
            title="Charla: Cómo exportar a Brasil",
            activity_type=Activity.Type.TALK,
            start=_at(0, 10),
            end=_at(0, 11),
            is_public=True,
            room="Auditorio A",
        )
        Activity.objects.create(
            event=ronda,
            title="Ronda de negocios (mesas)",
            activity_type=Activity.Type.BUSINESS_ROUND,
            start=_at(0, 11),
            end=_at(0, 13),
            is_public=False,
            room="Salón de mesas",
        )
        # Día 2
        Activity.objects.create(
            event=ronda,
            title="Exposición de productos",
            activity_type=Activity.Type.EXHIBITION,
            start=_at(1, 10),
            end=_at(1, 12),
            is_public=True,
            room="Pabellón A",
        )
        Activity.objects.create(
            event=ronda,
            title="Charla: Financiamiento para pymes",
            activity_type=Activity.Type.TALK,
            start=_at(1, 14),
            end=_at(1, 15),
            is_public=True,
            room="Auditorio B",
        )

        # Campos autoritativos de la ronda (por si el evento ya existía).
        ronda.general_price = 0
        ronda.capacity = 50
        ronda.status = Event.Status.PUBLISHED
        ronda.tables_count = 8
        ronda.meeting_duration_minutes = 30
        ronda.round_start_time = datetime.time(9, 0)
        ronda.round_end_time = datetime.time(12, 0)
        ronda.save()

        expo, _ = Event.objects.get_or_create(
            slug="expo-industrial-2026",
            defaults={
                "organization": org,
                "name": "Expo Industrial 2026",
                "event_type": Event.Type.FAIR,
                "modality": Event.Modality.IN_PERSON,
                "start_date": today + datetime.timedelta(days=45),
                "end_date": today + datetime.timedelta(days=47),
                "location": "Centro de Convenciones",
                "description": "Feria abierta al público con stands, charlas y networking.",
            },
        )
        expo.organization = org
        expo.name = "Expo Industrial 2026"
        expo.status = Event.Status.PUBLISHED
        expo.is_public = True
        expo.general_price = 2500
        expo.capacity = 200
        expo.save()

        self._seed_registrations(ronda, expo)
        self._seed_round(ronda)
        self._seed_attendances(ronda)
        self._seed_accreditations(ronda)

    def _seed_registrations(self, ronda, expo):
        """Inscribe algunas empresas y el asistente para tener datos de demo."""
        from apps.registrations.services import register_user_to_event

        emails = ["agrotech@demo.com", "metalurgica@demo.com", "asistente@demo.com"]
        for email in emails:
            user = User.objects.filter(email=email).first()
            if user:
                register_user_to_event(user=user, event=ronda)
        # Una inscripción paga (simulada) del asistente a la expo.
        attendee = User.objects.filter(email="asistente@demo.com").first()
        if attendee:
            register_user_to_event(user=attendee, event=expo)

    def _seed_round(self, ronda):
        """Genera el cronograma y una reunión confirmada de ejemplo."""
        from apps.companies.services import get_or_create_company_for_user
        from apps.events.services import generate_event_schedule
        from apps.meetings.services import (
            MeetingError,
            accept_meeting_request,
            request_meeting,
        )

        # Limpia bloques/reuniones previas y regenera desde la franja de la ronda.
        ronda.time_blocks.all().delete()  # cascade elimina meetings viejas
        generate_event_schedule(ronda)

        agro = User.objects.filter(email="agrotech@demo.com").first()
        metal = User.objects.filter(email="metalurgica@demo.com").first()
        block = ronda.time_blocks.first()
        if agro and metal and block:
            ca = get_or_create_company_for_user(agro)
            cm = get_or_create_company_for_user(metal)
            try:
                req = request_meeting(
                    event=ronda,
                    from_company=ca,
                    to_company=cm,
                    time_block=block,
                    message="Nos interesa conversar sobre proveeduría.",
                )
                if req.status == req.Status.PENDING:
                    accept_meeting_request(request=req)
            except MeetingError:
                pass

    def _seed_attendances(self, ronda):
        """Marca asistencia a algunas actividades para poblar agendas de demo."""
        from apps.agenda.models import ActivityAttendance
        from apps.agenda.services import AgendaError, toggle_activity_attendance

        talks = ronda.activities.filter(is_public=True)
        plan = {
            "agrotech@demo.com": ["Charla: Cómo exportar a Brasil", "Exposición de productos"],
            "asistente@demo.com": [
                "Charla: Cómo exportar a Brasil",
                "Charla: Financiamiento para pymes",
            ],
        }
        for email, titles in plan.items():
            user = User.objects.filter(email=email).first()
            if not user:
                continue
            for title in titles:
                activity = talks.filter(title=title).first()
                if (
                    activity
                    and not ActivityAttendance.objects.filter(user=user, activity=activity).exists()
                ):
                    try:
                        toggle_activity_attendance(user=user, activity=activity)
                    except AgendaError:
                        pass

    def _seed_accreditations(self, ronda):
        """Crea representantes y credenciales de demo (con una ya con ingreso)."""
        from apps.accreditation.models import Participant
        from apps.accreditation.services import (
            accredit_participant,
            check_in,
            get_or_create_self_accreditation,
        )
        from apps.companies.services import get_or_create_company_for_user
        from apps.registrations.models import Registration

        reps = {
            "agrotech@demo.com": [("Martín", "Gómez", "Gerente Comercial")],
            "metalurgica@demo.com": [("Lucía", "Fernández", "Directora de Ventas")],
        }
        for email, people in reps.items():
            user = User.objects.filter(email=email).first()
            reg = Registration.objects.filter(event=ronda, user=user).first()
            if not (user and reg):
                continue
            company = get_or_create_company_for_user(user)
            get_or_create_self_accreditation(reg)
            for first, last, cargo in people:
                participant, _ = Participant.objects.get_or_create(
                    company=company,
                    first_name=first,
                    last_name=last,
                    defaults={"cargo": cargo},
                )
                accredit_participant(registration=reg, participant=participant)

        # Un ingreso ya registrado (para ver control de asistencia).
        agro = User.objects.filter(email="agrotech@demo.com").first()
        reg = Registration.objects.filter(event=ronda, user=agro).first()
        if reg:
            check_in(get_or_create_self_accreditation(reg))

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
