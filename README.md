# RondaNegocios

Plataforma de Vinculación Empresarial y Rondas de Negocios (SaaS). Ver
`Idea-de-proyecto.txt` para la especificación funcional completa.

## Stack

- Python 3.12 (gestionado con [uv](https://docs.astral.sh/uv/))
- Django 4.2 LTS
- PostgreSQL 12+

## Instalación local

1. Instalar Python 3.12 y crear el entorno virtual:

   ```bash
   uv python install 3.12
   uv venv --python 3.12 .venv
   source .venv/bin/activate
   ```

2. Instalar dependencias:

   ```bash
   uv pip install -r requirements/dev.txt
   ```

3. Copiar `.env.example` a `.env` y completar los valores (`SECRET_KEY`,
   `DATABASE_URL`, etc.):

   ```bash
   cp .env.example .env
   ```

4. Crear la base de datos en PostgreSQL (ajustar usuario/clave/puerto según
   corresponda) y configurar `DATABASE_URL` en `.env`.

5. Aplicar migraciones y crear un superusuario:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Levantar el servidor de desarrollo:

   ```bash
   python manage.py runserver
   ```

## Estructura

```
config/            configuración del proyecto (settings/base|dev|prod, urls, wsgi/asgi)
apps/               apps de Django del dominio (accounts, ...)
requirements/       dependencias separadas por entorno (base/dev/prod)
static/, media/     archivos estáticos y de usuario
templates/          templates globales
```

`DJANGO_SETTINGS_MODULE` apunta a `config.settings.dev` por defecto
(`manage.py`) y a `config.settings.prod` en `wsgi.py`/`asgi.py`.

## Calidad de código

```bash
pre-commit install   # una sola vez
pre-commit run --all-files
```

## Tests

```bash
pytest
```
