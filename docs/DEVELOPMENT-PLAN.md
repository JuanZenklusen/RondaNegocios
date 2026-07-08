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

## Fase 3 — Empresas (perfil tipo LinkedIn)

- [ ] App `companies`: modelos `Company`, `Rubro`, `Product`, `Service`, `Need`
- [ ] Perfil completo (razón social, CUIT, logo, descripción, rubro, web, redes,
      dirección, localidad/provincia/país, empleados, capacidad, certificaciones)
- [ ] Carga de logo/imágenes (media)
- [ ] Edición de perfil (formularios crispy, responsive)
- [ ] **Perfil público** de la empresa (URL amigable, SEO, sin login)
- **Validación**: crear una empresa completa, editarla, ver su perfil público en
  mobile y desktop.

## Fase 4 — Networking / directorio

- [ ] Buscar y filtrar empresas (por rubro, ubicación, texto)
- [ ] Directorio paginado y responsive
- [ ] Guardar favoritos
- [ ] Solicitar contacto / conectar (sin exponer datos de contacto por ahora)
- **Validación**: buscar y filtrar con datos de prueba; agregar/quitar favoritos.

## Fase 5 — Gestión de eventos

- [ ] App `events`: modelo `Event` (tipos, fecha_inicio/fin, modalidad, ubicación,
      cupos, costos, estado), `Table` (mesas), `TimeBlock` (bloques horarios)
- [ ] CRUD de eventos para el rol organización
- [ ] Configuración de la ronda: duración de reunión y cantidad por empresa,
      eventos multi-día
- [ ] Listado público de próximos eventos
- **Validación**: crear un evento con mesas y bloques, verlo en el listado público.

## Fase 6 — Inscripciones

- [ ] App `registrations`: modelo `Registration`
- [ ] Inscripción online de empresa a un evento
- [ ] Gestión de cupos, estados (pendiente/validada/rechazada)
- [ ] Validación automática y manual
- **Validación**: inscribir una empresa, agotar cupo, aprobar/rechazar.

## Fase 7 — Pagos (Mercado Pago) + Planes

- [ ] App `payments`: modelos `Plan`, `Subscription`, `Payment`
- [ ] Integración Checkout Pro de Mercado Pago (credenciales por `.env`)
- [ ] Flujo: pago → redirect a MP → vuelta al sitio con validación (webhook +
      back_urls) → inscripción/matriculación automática
- [ ] Planes Gratuito / Profesional / Corporativo
- **Validación**: pago de prueba con credenciales sandbox de MP, confirmar que la
  inscripción queda automática al aprobarse.

## Fase 8 — Solicitudes de reunión y agenda

- [ ] App `meetings`: modelos `MeetingRequest`, `Meeting`
- [ ] Empresa A solicita reunión a B en un horario → reserva en agenda de ambos
- [ ] B acepta → confirmada, se asigna mesa + bloque horario; rechazar / reprogramar
      / cancelar
- [ ] Agenda por empresa (vista de slots confirmados/pendientes, estilo del modelo)
- [ ] Evitar conflictos (misma empresa/mesa/bloque no se solapan)
- **Validación**: flujo completo A→B con dos empresas de prueba, ver la agenda
  actualizarse y la mesa asignada; tests de no-solapamiento.

## Fase 9 — Motor de matching inteligente

- [ ] Algoritmo de scoring: productos/servicios ofrecidos vs necesidades, rubro,
      ubicación, intereses → `Match` con `score`
- [ ] Ranking de compatibilidad y sugerencias de reunión (badge de % match)
- [ ] Recalcular al cambiar perfiles/necesidades
- **Validación**: con empresas de prueba complementarias, ver que aparecen como
  sugerencias con score coherente; tests del cálculo de score.

## Fase 10 — Agenda inteligente (generación automática)

- [ ] Generación automática de agenda optimizada (disponibilidad, compatibilidades,
      mesas y bloques libres, duración configurable)
- [ ] Objetivos: maximizar reuniones, evitar conflictos, optimizar recursos
- **Validación**: generar una agenda para un evento con varias empresas y verificar
  que no hay conflictos y se maximizan los encuentros.

## Fase 11 — Participantes y acreditaciones

- [ ] App `accreditation`: modelos `Participant`, `Accreditation`
- [ ] Empresa crea representantes/participantes
- [ ] Generación automática de credenciales con **QR** e info
- [ ] Check-in / check-out y control de asistencia
- **Validación**: generar credencial con QR, simular check-in.

## Fase 12 — Mensajería y notificaciones

- [ ] App `notifications`: notificaciones internas + email
- [ ] Eventos que disparan notificación: nuevo match, reunión aprobada, cambio de
      agenda, pago confirmado
- [ ] Mensajería interna (mensajes directos, solicitudes de contacto)
- **Validación**: disparar cada tipo de notificación y verla en la campanita + email
  de consola.

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
