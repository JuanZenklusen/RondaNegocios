# RondaNegocios — Guía del proyecto para Claude

> Este archivo se carga en cada sesión. Contiene las convenciones y decisiones
> que **no** hay que volver a explicar. La especificación funcional completa está
> en `Idea-de-proyecto.txt`. El plan de desarrollo por fases está en
> `docs/DEVELOPMENT-PLAN.md` — **leerlo al empezar cada sesión** para saber en qué
> fase estamos.

## Qué es

Plataforma SaaS de vinculación empresarial y rondas de negocios: organizaciones
crean eventos (rondas presenciales, ferias, congresos), las empresas arman su
perfil (tipo LinkedIn), se inscriben, gestionan una agenda de reuniones B2B con
asignación de mesas, reciben sugerencias de un motor de matching, y acceden con
credenciales QR. Pagos vía Mercado Pago. Multi-organización (por ahora una sola,
pero la estructura queda lista para escalar).

## Stack y entorno

- **Python 3.12** gestionado con `uv` (binario en `~/.local/bin`, se activa con
  `source $HOME/.local/bin/env`). El venv del proyecto está en `.venv/`.
- **Django 4.2 LTS** (NO 5.x: el PostgreSQL local es la v12, que Django 5.2 no
  soporta — pide 14+).
- **PostgreSQL 12** corriendo en `localhost:5433`, base `rondanegocios_db`.
- `DJANGO_SETTINGS_MODULE`: `config.settings.dev` (default en `manage.py`),
  `config.settings.prod` en `wsgi.py`/`asgi.py`.
- Correr comandos: `source .venv/bin/activate` primero. Instalar paquetes con
  `source $HOME/.local/bin/env && uv pip install <pkg>` (no usar `pip` a secas).

## Arquitectura (decisión tomada: HÍBRIDO)

- **Ahora**: Django renderizado en servidor (MPA) con **autenticación por sesión**
  (cookies `HttpOnly` + `Secure` + `SameSite`). Templates Django + Bootstrap 5.
  Es lo más rápido, seguro y con buen SEO para los perfiles públicos de empresas.
- **Después**: se agrega **Django REST Framework** con auth por token SOLO donde
  haga falta (scanner de check-in QR, futura app mobile, integraciones). No se
  duplica el frontend desde el día uno.
- Regla clave: la lógica de negocio va en una **capa de servicios**
  (`apps/<app>/services.py`), no en las vistas ni pegada a los templates. Así el
  día que se exponga por API, la lógica ya está desacoplada y se reutiliza.
- Usar urls limpias, sin id ni información sensible. De ser necesario, utilizar
  slugs

## Estructura de código

```
config/settings/{base,dev,prod}.py   configuración por entorno (django-environ)
apps/<app>/                          apps del dominio; AppConfig con label corto
  models.py        modelos (datos + validación de invariantes)
  services.py      lógica de negocio / casos de uso (crear reunión, calcular match…)
  selectors.py     consultas de lectura complejas (opcional, cuando crezcan)
  forms.py         formularios
  views.py         vistas finas: validan input, llaman a services, renderizan
  urls.py          con app_name para namespacing
  admin.py         registro en el admin de Django
  tests/           tests con pytest-django
templates/           base.html + partials globales; por-app en apps/<app>/templates
static/              CSS/JS propios; assets del sistema de diseño
docs/                DEVELOPMENT-PLAN.md y documentación de arquitectura
```

## Convenciones de código

- **Vistas finas, modelos con comportamiento, lógica en `services.py`.** Una vista
  no debe tener reglas de negocio ni queries complejas inline.
- **Nombres**: clases y campos de modelo en **inglés** (convención Django:
  `Company`, `Event`, `Meeting`, `role`), con `verbose_name`/`verbose_name_plural`
  en **español** para el admin y la UI. Todo lo que ve el usuario final va en
  español (es-ar). El `User` ya sigue esto.
- **Multi-tenant**: todo modelo del dominio cuelga (directa o indirectamente) de
  `Organization`. Filtrar SIEMPRE por la organización del usuario; nunca exponer
  datos de otra organización. Preparar un manager/mixin de scoping desde el inicio
  aunque hoy haya una sola org.
- **Formularios**: usar `django-crispy-forms` + `crispy-bootstrap5` para que los
  forms salgan responsive y consistentes con el diseño (instalar cuando arranque
  la Fase 1).
- **Migraciones**: revisar cada migración generada antes de aplicarla. Uná
  migraciones triviales cuando tenga sentido; no dejar migraciones basura.
- **Tests**: cada feature con lógica de negocio se valida con al menos un test de
  `services.py`. Correr `pytest` antes de cerrar una fase.
- **i18n / zona horaria**: `LANGUAGE_CODE = "es-ar"`,
  `TIME_ZONE = "America/Argentina/Buenos_Aires"`, `USE_TZ = True`. Guardar todo en
  UTC, mostrar en hora local.
- **Secretos**: nunca hardcodear. Todo a `.env` (y documentado en `.env.example`).
- **Seguridad**: aprovechar el sistema de permisos de Django. CSRF siempre activo
  en formularios. Validar permisos por rol en cada vista sensible.

## Sistema de diseño (basado en `modelo-frontend.html`)

Estilo: **Glassmorphism** corporativo premium, **mobile-first**, 100% responsive
(el 90% de los usuarios entra desde el celular — el mobile NO es una adaptación,
es el diseño primario; el desktop es la ampliación).

**Librerías** (por CDN al inicio; vendorizar para prod más adelante):
- Bootstrap 5.3.2
- Font Awesome 6.4
- Fuente **Inter** (300–700) de Google Fonts
- **SweetAlert2** para TODAS las confirmaciones, alertas y mensajes al usuario
  (requisito de la spec — no usar `alert()` ni los toasts nativos salvo casos
  menores).

**Tokens de color** (definir como variables CSS en `static/css/design-system.css`):
```css
:root {
  --glass-bg:      rgba(255, 255, 255, 0.45);
  --glass-border:  rgba(255, 255, 255, 0.6);
  --glass-shadow:  rgba(31, 38, 135, 0.05);
  --text-main:     #1e293b;   /* slate-800  */
  --text-muted:    #64748b;   /* slate-500  */
  --accent-blue:   #2563eb;   /* primario   */
  --accent-pink:   #d946ef;   /* secundario */
  --dark:          #0f172a;   /* sidebar activo, botones oscuros */
  --success:       #10b981;   /* confirmado */
  --warning:       #f59e0b;   /* pendiente  */
}
/* Fondo global de la app */
body {
  font-family: 'Inter', sans-serif;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 30%, #a5f3fc 70%, #e0f2fe 100%);
  background-attachment: fixed;
  color: var(--text-main);
}
```

**Componentes reutilizables** (extraídos del modelo — crear como partials/CSS):
- `.glass-dashboard-wrapper` — contenedor principal, `backdrop-filter: blur(20px)`,
  `border-radius: 24px`.
- `.glass-card` — tarjeta de contenido, `blur(12px)`, `border-radius: 20px`, hover
  que eleva (`translateY(-3px)`).
- `.premium-blue-card` — tarjeta destacada, degradado
  `linear-gradient(135deg, #38bdf8 0%, #0369a1 100%)`, texto blanco (se usa para
  la credencial corporativa).
- `.glass-sidebar` + `.sidebar-link` (con estado `.active` fondo `--dark`) — menú
  lateral; **en mobile debe colapsar** a un menú hamburguesa / offcanvas de
  Bootstrap.
- `.glass-navbar` — barra superior con logo, búsqueda, notificaciones, avatar.
- `.badge-glass-match` — badge de % de match del motor de sugerencias.
- `.agenda-row` con variantes `.confirmed` (borde izq. verde) y `.pending` (borde
  izq. ámbar) — filas de la agenda de reuniones.
- `.qr-box` — contenedor de credencial QR.

**Reglas mobile-first**:
- Diseñar el layout base para viewport chico primero; usar breakpoints de
  Bootstrap (`col-12` → `col-md-*` → `col-lg-*`) para expandir.
- Áreas táctiles cómodas (botones con padding generoso, ya visto en el modelo).
- El sidebar es lateral en desktop pero offcanvas/hamburguesa en mobile.
- Probar cada pantalla a ~375px de ancho antes de darla por terminada.

## Flujo de trabajo por sesión

1. Leer `docs/DEVELOPMENT-PLAN.md` para ubicar la fase actual.
2. Trabajar la fase, con lógica en `services.py` y tests.
3. **Validar con pruebas** (levantar el server, ejercitar el flujo, `pytest`)
   antes de dar algo por cerrado. No cerrar una fase sin verla funcionar.
4. Marcar los checkboxes completados en el plan.
5. Commits atómicos y descriptivos (pre-commit corre black/isort/ruff automático).
6. Las sesiones/tokens se agotan: dejar el plan actualizado para retomar sin
   perder contexto.

## Estado actual

**Fases 0-6 + 8-12 completas** (129 tests verdes; la Fase 7 —pagos MP— se pospuso). Fase 0: shell de UI. Fase 1: auth
(**login por email**). Fase 2: multi-tenant — `Organization`, base abstracta
**`OrganizationScopedModel`** (heredarla en todo modelo del dominio) con
`.for_user(user)`, `User.organization`, org por defecto (`slug="principal"`),
mixins `OrganizationScopedQuerysetMixin`/`OrganizationFormMixin`. Fase 3: app
`companies` — `Company` (scoped, OneToOne User), `Rubro`/`Product`/`Service`/`Need`,
validador **CUIT**, edición crispy + inline formsets, perfil público `/empresa/<slug>/`.
Fase 4: app `networking` — `Favorite`, `ConnectionRequest`, directorio con
búsqueda/filtros, endpoints JSON (fetch+CSRF). `_MyCompanyMixin` da `self.my_company`.
Fase 5: app `events` — `Event` (scoped), `Activity` (programa), `Table`, `TimeBlock`;
CRUD organizador (inline formset de actividades); listado/detalle público. Nuevo rol
**`attendee`** (público) con su registro. Fase 6: app `registrations` —
`Registration` (event+user, estados, pago); inscripción de empresas y asistentes
(cupos vía `Event.capacity`/`is_full`, aprobación auto o manual con
`Event.requires_approval`); **pago SIMULADO** (`payment=simulated`, sin pasarela;
Mercado Pago = fase posterior); "Mis inscripciones" + gestión del organizador.
Fase 8: app `meetings` — `MeetingRequest`/`Meeting`; organizador genera cronograma
(`events.services.generate_event_schedule` crea `Table`/`TimeBlock` desde
`round_start_time`/`round_end_time`); empresa confirmada solicita reunión → la otra
acepta → `Meeting` con **mesa asignada automáticamente** y **anti-solapamiento**
(empresa/mesa por bloque); agenda por empresa en `/eventos/<slug>/ronda/`.
Fase 9: app `matching` — `Match` (score 0-100); scoring por complementariedad
oferta↔necesidad (70%) + rubro (15%) + provincia (15%) en `scoring.py`;
`recompute_company_matches` (al guardar perfil) / `recompute_all` / command
`recompute_matches`; `top_matches_for`/`match_scores_map`; sugerencias en dashboard,
badge de % match en directorio y ronda. Filtro template `core_extras.dict_get`.
Fase 10: app `agenda` — `ActivityAttendance`; **agenda personal por evento** en
`/eventos/<slug>/mi-agenda/` donde el inscripto elige a qué actividades asiste
(toggle) y la agenda se autocompleta con actividades + reuniones confirmadas
(`selectors.personal_agenda`, programa multi-día). Los `TimeBlock` de la ronda se
derivan de la ventana de la actividad "Ronda de negocios"
(`events.services.generate_event_schedule` / `_round_windows`).
Fase 11: app `accreditation` — `Participant` (representantes de empresa) y
`Accreditation` (credencial con `code` único, check-in/out). Credencial digital con
**QR** (lib `qrcode`, PNG on-the-fly en `QRView`, el QR apunta a la URL de check-in);
empresa acredita representantes, asistente tiene credencial propia; organizador
escanea y registra ingreso/egreso. Sidebar "Credenciales".
Fase 12: app `notifications` — `Notification` (campanita) y `Message` (mensajería
directa). `services.notify()` (interna + email opcional) disparado desde
meetings/networking/registrations (import lazy para evitar circular);
`send_message()`; `context_processors.notifications` alimenta navbar
(`nav_unread_notifications`/`nav_unread_messages`/`nav_recent_notifications`).

**Roles**: superadmin, organization, company, representative, attendee.
**Manual de usuario**: `docs/MANUAL-USUARIO.md` — actualizar al cerrar cada fase.

**Notas del entorno**: (1) login por **email**. (2) `runserver` NO puede bindear
puerto en el sandbox — validar con test client (`Client(SERVER_NAME='localhost')`).
(3) Django fijado en **4.2** (Postgres 12); pinnear paquetes que arrastren Django 5/6.
(4) Pillow instalado. (5) Datos demo: `python manage.py seed_demo` (empresas/eventos
ficticios); credenciales en `CREDENCIALES-DEMO.txt` (git-ignored).

**Próximo: Fase 13 (dashboards y reportes con métricas reales).** Fase 7 (pagos
Mercado Pago) pospuesta por decisión del usuario. Ver `docs/DEVELOPMENT-PLAN.md`.
