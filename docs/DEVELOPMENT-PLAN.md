# Plan de desarrollo — RondaNegocios

Roadmap por fases, ordenado por dependencias. Cada fase termina en algo
**validable** (se puede probar y demostrar funcionando). No avanzar a la siguiente
sin validar la actual. Marcar los checkboxes a medida que se completan.

Leyenda: `[ ]` pendiente · `[~]` en progreso · `[x]` hecho y validado.

Convenciones y sistema de diseño: ver `CLAUDE.md`. Spec funcional: `Idea-de-proyecto.txt`.

---

## Fase 0 — Fundamentos ✅

- [x] Entorno (uv, Python 3.12, venv), Django 4.2, PostgreSQL, settings por entorno
- [x] Custom User model con `role`
- [x] Requirements separados, pre-commit, pytest-django, README
- [x] Shell de UI base: `templates/base.html` con bloques, `app_base.html` con
      navbar + sidebar responsive (offcanvas-lg en mobile), partials en
      `templates/partials/`, `static/css/design-system.css` con tokens y
      componentes glass
- [x] App `core` con landing pública (`/`) y dashboard demo (`/app/`)
- [x] Integrados SweetAlert2, Bootstrap 5.3, Font Awesome, Inter; mensajes de
      Django enrutados a toasts de SweetAlert2
- **Validación**: rutas responden 200 sin errores; falta el eyeball visual del
  usuario a 375px y desktop (abrir `/` y `/app/`).

## Fase 1 — Autenticación y cuentas ✅

- [x] Instalar `django-crispy-forms` + `crispy-bootstrap5`
- [x] **Login por email** (no username): `USERNAME_FIELD="email"` + `UserManager`
      custom; migración aplicada
- [x] Registro de empresa (alta de User rol `company` + datos mínimos), con
      `services.register_company_user`
- [x] Login / logout con sesión
- [x] Recuperación de contraseña por email (backend de consola en dev)
- [x] Mixins de permisos por rol (`RoleRequiredMixin`, `CompanyRequiredMixin`,
      `OrganizationRequiredMixin`); dashboard protegido con login
- [x] Perfil de usuario (ver/editar datos propios)
- [x] Admin del User adaptado a email
- [x] 12 tests (services, vistas, mixins) — todos verdes
- **Validación**: hecha vía test client (GET de todas las pantallas de auth = 200,
  flujo registro→login→dashboard→perfil→reset). Falta eyeball visual del usuario.

## Fase 2 — Organizaciones y multi-tenant ✅

- [x] Instalar Pillow (ImageField para logos)
- [x] App `organizations`: modelo `Organization`
- [x] `OrganizationScopedModel` (base abstracta) + `OrganizationScopedQuerySet`
      con `.for_user(user)` (superadmin ve todo, usuario ve su org, sin org no ve nada)
- [x] Vincular `User` a `Organization` (FK nullable, `SET_NULL`)
- [x] Data migration con la organización inicial (`slug="principal"`)
- [x] `register_company_user` asocia a la organización por defecto
- [x] Admin de `Organization` + FK org en admin de User
- [x] Mixins de vistas: `OrganizationScopedQuerysetMixin`, `OrganizationFormMixin`
- [x] Tests de aislamiento (5 nuevos) — 17 en total, verdes
- **Validación**: test de scoping (usuario org A no ve datos de org B; superadmin ve
  todo; sin org no ve nada) + validación funcional del seed y registro. Los modelos
  del dominio (Fase 3+) heredarán de `OrganizationScopedModel`.

## Fase 3 — Empresas (perfil tipo LinkedIn) ✅

- [x] App `companies`: modelos `Company` (hereda `OrganizationScopedModel`),
      `Rubro`, `Product`, `Service`, `Need`
- [x] Validador de **CUIT** con dígito verificador (`validators.py`)
- [x] Perfil completo (razón social, nombre fantasía, CUIT, logo, descripción,
      rubro, web, redes, dirección, localidad/provincia/país, empleados,
      capacidad productiva, certificaciones, `is_public`)
- [x] Carga de logo (media, Pillow) + slug público autogenerado y único
- [x] Edición de perfil con **crispy** + **inline formsets** (productos/servicios/
      necesidades) con "Agregar fila" por JS; lógica de get-or-create en `services.py`
- [x] **Perfil público** SEO en `/empresa/<slug>/` (sin login, respeta `is_public`)
- [x] Seed de 15 rubros; admin con inlines
- [x] 14 tests nuevos (validador CUIT, modelo, vistas, público/privado) — 31 en total
- **Validación**: hecha vía test client (edición crea company, guarda formsets,
  rechaza CUIT inválido, perfil público 200 / privado 404). Falta eyeball visual.

## Fase 4 — Networking / directorio ✅

- [x] App `networking`: modelos `Favorite` y `ConnectionRequest` (unique
      constraints)
- [x] Directorio paginado (12/pág) y responsive, scopeado por organización, sólo
      perfiles públicos, excluye la propia empresa (`selectors.search_companies`)
- [x] Búsqueda por texto (razón social/fantasía/descripción/productos/servicios)
      y filtros por rubro y provincia
- [x] Favoritos: toggle vía endpoint JSON (fetch + CSRF) + página de favoritos
- [x] Solicitar conexión (endpoint JSON con confirmación SweetAlert2) + página de
      conexiones (recibidas: aceptar/rechazar; enviadas con estado). Sin compartir
      datos de contacto todavía.
- [x] Admin, sidebar "Red de Empresas" conectado, 15 tests nuevos — 45 en total
- **Validación**: hecha vía test client (búsqueda/filtros, favoritos add/remove,
  conexión enviar→aceptar, scoping de permisos). Falta eyeball visual.

## Fase 5 — Gestión de eventos ✅

- [x] Nuevo rol **`attendee`** (público general) + registro de asistente
- [x] App `events`: `Event` (scoped; tipos, modalidad, estado, fechas multi-día,
      ubicación, cupo, precio, config de ronda), `Activity` (programa: charlas,
      exposiciones, reuniones públicas…), `Table`, `TimeBlock`
- [x] CRUD de eventos para rol organización (list/create/update/delete) con
      actividades vía inline formset; scopeado por organización
- [x] Listado público de próximos eventos + detalle público con el programa
- [x] Botón **"Inscribirme"** provisorio (pago **simulado** con SweetAlert; la
      integración real de Mercado Pago es fase posterior)
- [x] Sidebar: "Eventos" (todos) y "Gestión de eventos" (solo organizadores)
- [x] 13 tests nuevos — 58 en total
- **Validación**: hecha vía test client (crear evento con actividad, visibilidad
  pública según estado/is_public, permisos por rol). Falta eyeball visual.
- Nota: generación automática de mesas/bloques y la agenda se harán en la Fase 8.

## Fase 6 — Inscripciones ✅

- [x] App `registrations`: modelo `Registration` (event+user, estados, pago)
- [x] Inscripción online de **empresa y asistente** a un evento (desde el detalle
      público, botón real → POST)
- [x] Gestión de **cupos** (`Event.capacity`/`taken_slots`/`is_full`) y estados
      (pendiente/confirmada/rechazada/cancelada)
- [x] **Validación automática** (confirma al toque) o **manual** (queda pendiente
      si `Event.requires_approval`), con aprobar/rechazar del organizador
- [x] **Pago simulado**: eventos pagos marcan `payment=simulated` (sin pasarela real)
- [x] Página "Mis inscripciones" (cancelar) + gestión de inscripciones por evento
- [x] 16 tests nuevos — 74 en total; seed con inscripciones de demo
- **Validación**: hecha vía test client (gratis/pago/aprobación/cupo/cancelar,
  permisos). Falta eyeball visual.

## Fase 7 — Pagos (Mercado Pago) + Planes

- [ ] App `payments`: modelos `Plan`, `Subscription`, `Payment`
- [ ] Integración Checkout Pro de Mercado Pago (credenciales por `.env`)
- [ ] Flujo: pago → redirect a MP → vuelta al sitio con validación (webhook +
      back_urls) → inscripción/matriculación automática
- [ ] Planes Gratuito / Profesional / Corporativo
- **Validación**: pago de prueba con credenciales sandbox de MP, confirmar que la
  inscripción queda automática al aprobarse.

## Fase 8 — Solicitudes de reunión y agenda ✅

- [x] Generación de cronograma (mesas + bloques) desde config de la ronda
      (`events.services.generate_event_schedule`; pendiente de Fase 5) + horarios
      de ronda en `Event`
- [x] App `meetings`: modelos `MeetingRequest`, `Meeting`
- [x] Empresa A solicita reunión a B en un bloque → queda pendiente en ambas
- [x] B acepta → **Meeting confirmada con mesa asignada automáticamente**; rechazar
      / cancelar
- [x] Agenda por empresa (bloques con reunión confirmada/libre) + solicitudes
      recibidas/enviadas (`selectors.py`)
- [x] **Anti-solapamiento**: una empresa no tiene 2 reuniones en el mismo bloque;
      una mesa no se reasigna en el mismo bloque; no hay reunión duplicada por pareja
- [x] Acceso a la ronda solo con inscripción confirmada; 16 tests nuevos — 88 en total
- **Validación**: flujo completo A→B validado vía test client (solicitar→aceptar→
      agenda con mesa) + tests de conflictos y de agotamiento de mesas. Seed con
      cronograma + reunión de ejemplo. Falta eyeball visual.
- Nota: la **generación automática/optimizada** de agenda es la Fase 10.

## Fase 9 — Motor de matching inteligente ✅

- [x] App `matching`: modelo `Match` (par único, `score` 0-100, `details` JSON)
- [x] Algoritmo de scoring (`scoring.py`): complementariedad oferta↔necesidad
      (70%) + rubro (15%) + provincia (15%), con tokenización y stopwords
- [x] Recálculo: `services.recompute_company_matches` (al guardar perfil) y
      `recompute_all` + management command `recompute_matches`
- [x] Ranking y sugerencias: `selectors.top_matches_for` / `match_scores_map`
- [x] Integración UI: **sugerencias en el dashboard**, **badge de % match** en el
      directorio y en la ronda (participantes ordenados por compatibilidad)
- [x] 11 tests nuevos — 95 en total; seed recalcula matches (par MetalParaná ↔
      Logística Andina = 35%)
- **Validación**: tests del scoring (complementarias→alto, no relacionadas→0, bonus
  rubro/provincia) + funcional del dashboard/directorio. Falta eyeball visual.

## Fase 10 — Agenda personal del inscripto ✅

> Reformulada según pedido del usuario: cada inscripto elige a qué partes del
> evento asiste y la agenda se autocompleta (además de sus reuniones de la ronda).

- [x] App `agenda`: modelo `ActivityAttendance` (asistencia por usuario+actividad)
- [x] **Programa multi-día**: actividades agrupadas por día (`selectors.program_by_day`)
- [x] Elegir asistencia a cada actividad (toggle) con validaciones (inscripción
      confirmada; asistentes solo actividades públicas)
- [x] **Agenda autocompletada** (`selectors.personal_agenda`): combina actividades
      elegidas + reuniones confirmadas, cronológica por día/hora
- [x] Las reuniones de la ronda se coordinan **dentro de la franja de la actividad
      "Ronda de negocios"**: `generate_event_schedule` deriva los `TimeBlock` de la
      ventana de esa actividad (con fallback a `round_start_time`/`round_end_time`)
- [x] Link "Mi agenda" desde "Mis inscripciones"; botón "Coordinar reuniones" en la
      actividad de ronda
- [x] 10 tests nuevos — 105 en total; seed con programa de 2 días y asistencias demo
- **Validación**: flujo end-to-end (programa multi-día, toggle, agenda con reunión y
      mesa, permisos de asistente) + test de bloques dentro de la franja de la ronda.
- Nota: la generación **optimizada/automática** de reuniones (maximizar encuentros)
  queda como mejora futura; hoy la agenda se arma con elección manual + matching.

## Fase 11 — Participantes y acreditaciones ✅

- [x] App `accreditation`: modelos `Participant` (representantes de empresa) y
      `Accreditation` (credencial con `code`, check-in/out)
- [x] Empresa crea representantes y los **acredita** por evento; asistente obtiene
      su credencial propia (self) automáticamente
- [x] **Credencial digital con QR** (generado con `qrcode` como PNG on-the-fly;
      el QR apunta a la URL de check-in del organizador)
- [x] Check-in / check-out: el organizador escanea el QR → registra
      ingreso/egreso; lista de acreditaciones por evento con estado
- [x] Sidebar "Credenciales", link de acreditaciones en gestión de eventos
- [x] 11 tests nuevos — 116 en total; seed con representantes y credenciales
- **Validación**: flujo end-to-end (empresa acredita representante → credencial con
      QR PNG → organizador check-in) + permisos (QR oculto a extraños, empresa no
      hace check-in). Falta eyeball visual.

## Fase 12 — Mensajería y notificaciones ✅

- [x] App `notifications`: modelos `Notification` (alerta interna) y `Message`
      (mensaje directo)
- [x] `notify(...)` (interna + email opcional) y `send_message(...)` con service/
      selectors; context processor para los contadores de la navbar
- [x] Disparadores: solicitud de reunión, reunión confirmada (email), solicitud de
      conexión, inscripción aprobada/rechazada (email)
- [x] **Campanita** con contador + dropdown de recientes; página de notificaciones
      (marcar leídas); **sobre** con no leídos
- [x] Mensajería directa entre empresas: bandeja (inbox), conversación con envío,
      "Enviar mensaje" desde el directorio
- [x] 13 tests nuevos — 129 en total
- **Validación**: end-to-end (mensaje→notificación→campanita→leído) + tests de
      disparadores (reunión notifica, aprobación notifica + email). Falta eyeball.
- Nota: "cambio de agenda" y "pago confirmado" se conectarán cuando existan esos
  disparadores (pagos = Fase 7 pospuesta).

## Fase 13 — Dashboards y reportes

- [ ] Dashboard empresarial (reuniones, solicitudes, matches, eventos, contactos)
- [ ] Dashboard organizador (empresas registradas/acreditadas, pagos, eventos,
      reuniones, estadísticas)
- [ ] Reportes (participación, conversión, matching, facturación)
- **Validación**: dashboards con datos reales de las fases anteriores, responsive.

## Fase 14 — Capa API (Django REST Framework)

- [ ] Instalar y configurar DRF con auth por token
- [ ] Exponer endpoints donde realmente aporta: scanner de check-in QR, consumo
      mobile, integraciones
- [ ] Documentación de la API (drf-spectacular / OpenAPI)
- **Validación**: consumir un endpoint autenticado por token (ej: check-in) desde
  fuera del navegador.

## Fase 15 — Auditoría, seguridad y despliegue

- [ ] App `audit`: log de acciones (auditoría), logs de actividad
- [ ] Repaso de seguridad (permisos, HTTPS, headers, checklist de deployment Django)
- [ ] Gunicorn + Nginx + SSL
- [ ] Backups automáticos
- [ ] (Opcional) Dockerizar para alinear dev/prod
- **Validación**: correr `manage.py check --deploy` sin warnings críticos; desplegar
  en un entorno de prueba.

---

## Cómo retomar entre sesiones

Como las sesiones se agotan: al reabrir, leer este archivo, ubicar la primera fase
sin cerrar, y continuar desde ahí. Mantener los checkboxes al día es lo que permite
no perder contexto.
