# Manual de usuario — RondaNegocios

Guía de uso de la plataforma. Se va actualizando a medida que se agregan
funcionalidades. Última actualización: hasta la **Fase 12 (mensajería y avisos)**.

---

## 1. ¿Qué es RondaNegocios?

Es una plataforma para conectar empresas y organizar **rondas de negocios**,
ferias, charlas y otros eventos. Permite:

- Crear un **perfil de empresa** público (tipo LinkedIn).
- Descubrir otras empresas, guardarlas como favoritas y **conectar**.
- Ver y difundir **eventos** con su programa de actividades.
- (Próximamente) inscribirse a eventos, gestionar la agenda de reuniones,
  matching automático, credenciales con QR y pagos.

Está pensada para usarse **desde el celular** (es 100% responsive), aunque
funciona igual en tablet y computadora.

---

## 2. Tipos de cuenta (roles)

| Rol | Para quién | Qué puede hacer |
|-----|------------|-----------------|
| **Empresa** | Empresas que participan de las rondas | Perfil institucional, networking, inscribirse a eventos |
| **Asistente** | Público general | Inscribirse a eventos y participar de actividades abiertas (charlas, etc.) |
| **Organización** | Quien organiza los eventos (cámara, municipio…) | Crear y gestionar eventos y su programa |
| **Super administrador** | Dueño de la plataforma | Control total (vía panel de administración) |

---

## 3. Registro e ingreso

### Crear una cuenta de empresa
1. En la pantalla de inicio, tocá **"Registrar empresa"**.
2. Completá correo, nombre de contacto y contraseña.
3. Quedás logueado automáticamente y entrás al panel.

### Crear una cuenta de asistente (público)
1. Entrá a **"Registrate como asistente"** (link en la pantalla de registro o al
   intentar inscribirte a un evento).
2. Completá tus datos y listo.

### Ingresar
- El ingreso es **con tu correo electrónico** y contraseña.
- Si olvidaste la contraseña, usá **"¿Olvidaste tu contraseña?"**: te llega un
  correo con un enlace para restablecerla.

---

## 4. Perfil de empresa

Desde el menú lateral, **"Perfil Empresa"**. Ahí completás:

- **Datos institucionales**: razón social, nombre de fantasía, CUIT, rubro,
  descripción, logo, sitio web, redes sociales, ubicación, cantidad de empleados,
  capacidad productiva y certificaciones.
- **Productos**, **Servicios** y **Necesidades** (lo que tu empresa busca): se
  cargan con el botón **"Agregar"** de cada sección. Podés sumar todas las filas
  que quieras y eliminar las que no.

> El **CUIT** se valida automáticamente (incluye el dígito verificador), así que
> tiene que ser un CUIT real.

Cuando guardás, tu empresa tiene un **perfil público** con una dirección propia
(botón **"Ver perfil público"**). Ese perfil se puede compartir y lo ve cualquier
persona, sin necesidad de tener cuenta. Si no querés que sea público, destildá
**"Perfil público"**.

---

## 5. Red de empresas (networking)

Desde el menú **"Red de Empresas"**:

- **Buscá** empresas por nombre, producto o servicio.
- **Filtrá** por rubro y por provincia.
- Tocá la **estrella** para guardar una empresa en **Favoritos**.
- Tocá **"Conectar"** para enviar una solicitud de conexión (te pide confirmar).

En **"Conexiones"** ves:
- Las solicitudes **recibidas**, que podés **aceptar** o **rechazar**.
- Las solicitudes que **enviaste** y su estado.

> Por ahora, conectar registra el vínculo comercial pero **no comparte datos de
> contacto**. Eso puede cambiar más adelante.

### Sugerencias inteligentes (matching)
La plataforma calcula un **% de compatibilidad** entre empresas: es alto cuando lo
que una **ofrece** (productos/servicios) coincide con lo que la otra **busca**
(necesidades), y suma puntos por compartir rubro y provincia.

- En tu **Dashboard** ves las **empresas sugeridas** con mayor compatibilidad.
- En la **Red de empresas** y en la **ronda**, cada empresa muestra su **% match**.
- Completá bien tus **productos, servicios y necesidades**: cuanto más detallado tu
  perfil, mejores serán las sugerencias (se recalculan cada vez que lo guardás).

---

## 6. Eventos

### Ver eventos (todos los usuarios)
- Desde **"Eventos"** en el menú, o la página pública de próximos eventos.
- Cada evento muestra su **programa**: charlas, exposiciones, reuniones públicas
  y la ronda de negocios. Las actividades marcadas **"Abierta al público"** son
  para asistentes; las de **"Solo empresas"** son parte de la ronda.

### Inscribirse a un evento
1. En el detalle del evento, tocá **"Inscribirme"**.
2. Si el evento es **gratis**, confirmás y quedás inscripto.
3. Si tiene **costo**, se muestra un paso de pago (**simulado** por ahora) y luego
   quedás inscripto.
4. Si el organizador configuró **aprobación manual**, tu inscripción queda
   **pendiente** hasta que la apruebe.

Tus inscripciones las ves en **"Mis inscripciones"** (podés cancelarlas desde ahí).
Si el evento tiene **cupo** y se agota, no vas a poder inscribirte.

> ⚠️ **Pagos**: el pago todavía está **simulado** (no se cobra de verdad). La
> integración real con Mercado Pago se hace en una etapa posterior.

### Gestionar inscripciones (organizador)
Desde **"Gestión de eventos"**, el ícono de participantes de cada evento te lleva
a la lista de inscriptos, donde ves el cupo ocupado y podés **aprobar o rechazar**
las inscripciones pendientes.

### Organizar eventos (rol Organización)
Desde **"Gestión de eventos"** (solo visible para organizadores):

1. **"Nuevo evento"**: cargás nombre, tipo (ronda, feria, congreso…), modalidad
   (presencial/virtual/híbrido), fechas (puede durar varios días), lugar, cupo,
   precio de entrada y estado.
2. **Estado del evento**:
   - *Borrador*: no se ve en público.
   - *Publicado*: aparece en el listado de próximos eventos.
   - *Finalizado* / *Cancelado*.
3. **Programa / Actividades**: agregás las charlas, exposiciones, etc., cada una
   con su horario, sala y si es abierta al público.
4. **Configuración de la ronda**: duración de cada reunión, reuniones por empresa,
   cantidad de mesas y horarios de la ronda (ver sección 7).

Podés **editar** o **eliminar** un evento desde el listado de gestión.

---

## 7. Ronda de reuniones (agenda B2B)

Para las **rondas de negocios**, las empresas con inscripción **confirmada**
pueden agendar reuniones entre sí.

### Como organizador: preparar la ronda
1. Al editar el evento, definí la **duración de cada reunión**, la **cantidad de
   mesas** y los **horarios de la ronda** (hora de inicio y fin).
2. Tocá **"Generar cronograma"**: el sistema crea las **mesas** y los **bloques
   horarios** automáticamente (por ejemplo, de 9:00 a 12:00 en tramos de 30 min).

### Como empresa: agendar reuniones
1. Desde **"Mis inscripciones"**, en un evento de ronda confirmado, tocá
   **"Ir a la ronda"**.
2. En **"Solicitar reunión"** elegí una empresa participante y un **horario**
   libre, y enviá la solicitud.
3. La otra empresa la ve en **"Solicitudes recibidas"** y puede **aceptar** o
   **rechazar**.
4. Al aceptar, la reunión queda **confirmada** con una **mesa asignada
   automáticamente** y aparece en la agenda de ambas empresas.

El sistema **evita conflictos**: no vas a tener dos reuniones en el mismo horario,
ni se asignará una mesa ya ocupada en ese bloque. Podés **cancelar** una reunión
desde tu agenda (libera la mesa y el horario).

> Las reuniones se coordinan **dentro de la franja horaria de la actividad
> "Ronda de negocios (mesas)"** del programa. El organizador la genera con el botón
> "Generar cronograma".

---

## 8. Mi agenda del evento

Cada inscripto (empresa o asistente) tiene una **agenda personal** por evento, a la
que llega desde **"Mis inscripciones" → "Mi agenda"**.

- Ves el **programa completo** del evento, día por día (los eventos pueden durar
  varias jornadas).
- En cada actividad (charla, exposición, etc.) tocás **"Agregar a mi agenda"** o
  **"Quitar de mi agenda"**. Tu agenda se **autocompleta** con lo que elegís.
- Las actividades marcadas **"Abierta al público"** las puede sumar cualquier
  inscripto; las de **"Solo empresas"** (como la ronda de mesas) son para empresas.
- Si sos empresa, en la actividad **"Ronda de negocios (mesas)"** tenés el botón
  **"Coordinar reuniones"** que te lleva a la ronda; las reuniones que confirmes
  aparecen **automáticamente** en tu agenda, con su **mesa** y horario.

Así, tu cronograma final combina en un solo lugar las actividades que elegiste y
tus reuniones confirmadas, en orden por día y hora.

---

## 9. Credenciales y acreditación (QR)

Todos los inscriptos confirmados tienen una **credencial digital con código QR**
para acceder al evento. Se ven desde **"Credenciales"** en el menú.

### Empresas
- Cargá tus **representantes** (nombre, apellido, cargo, email, teléfono).
- Para cada evento confirmado, **acreditá** a los representantes que van a asistir:
  cada uno obtiene su **credencial con QR** propia. La empresa titular también tiene
  la suya.

### Asistentes
- Al confirmar tu inscripción, se genera automáticamente tu **credencial con QR**.

### En el acceso al evento (organizador)
- El organizador **escanea el QR** de cada credencial (o entra desde "Acreditaciones"
  del evento) y registra el **ingreso** y, si corresponde, el **egreso**.
- En **"Gestión de eventos" → ícono QR** ve la lista de acreditaciones con su estado
  (pendiente / ingresó / egresó).

> Mostrá tu credencial (el QR) desde el celular en el acceso; no hace falta imprimir.

---

## 10. Notificaciones y mensajes

### Notificaciones (la campanita 🔔)
Arriba a la derecha, la **campanita** te avisa de la actividad importante:
- Nuevas **solicitudes de reunión** y **reuniones confirmadas**.
- Nuevas **solicitudes de conexión**.
- **Inscripciones aprobadas** por el organizador.
- Nuevos **mensajes**.

El número rojo indica cuántas no leíste. Al tocar una notificación te lleva a la
sección correspondiente. Algunas (como una reunión confirmada o una inscripción
aprobada) también te llegan por **email**.

### Mensajes (el sobre ✉️)
Podés **escribirle a otra empresa** directamente:
- Desde el **directorio** ("Red de empresas"), con el ícono de mensaje de cada
  empresa.
- El sobre en la barra superior te lleva a tu **bandeja de mensajes**, con todas
  tus conversaciones y las no leídas.

---

## 11. Preguntas frecuentes

**¿Puedo entrar como empresa y como asistente con el mismo correo?**
No, cada correo es una sola cuenta. Usá correos distintos si necesitás ambos roles.

**¿Cómo me hago organizador?**
El rol de Organización lo asigna el administrador de la plataforma.

**No me aparece "Gestión de eventos".**
Ese menú es solo para cuentas de Organización.

---

*Este manual crece con el proyecto. Próximas secciones: inscripciones y pagos,
agenda de reuniones, matching, credenciales con QR.*
