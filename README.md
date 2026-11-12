# Centro de Día Proyectar - API

API REST para la gestión integral del Centro de Día Proyectar.

## Tecnologías

- **Backend**: Django 6.1 + Django REST Framework 3.18
- **Base de datos**: PostgreSQL (Supabase) / SQLite (desarrollo)
- **Autenticación**: JWT (SimpleJWT)
- **Documentación**: drf-spectacular (OpenAPI/Swagger)
- **Tests**: pytest + model-bakery
- **Storage**: Supabase Storage (S3 compatible) para producción / FileSystem (local)
- **Contenedores**: Docker + Gunicorn + WhiteNoise

## Configuración de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### Variables Principales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Django | (requerida) |
| `DEBUG` | Modo debug | `True` (dev) |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF confiables | `http://localhost:8000` |
| `DATABASE_URL` | URL de PostgreSQL (vacío = SQLite) | `` |
| `DJANGO_SETTINGS_MODULE` | Módulo de settings | `config.settings.development` |

### Base de Datos (PostgreSQL)

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### JWT

```env
JWT_ACCESS_LIFETIME=60        # minutos
JWT_REFRESH_LIFETIME=1440     # minutos (24hs)
```

## Storage de Media (Supabase)

### Configuración

El proyecto usa **Supabase Storage (S3 compatible)** solo en producción. En desarrollo local se usa el filesystem local (`MEDIA_ROOT`).

```env
# .env - Produccion
USE_SUPABASE_STORAGE=True
SUPABASE_S3_ACCESS_KEY=tu_access_key
SUPABASE_S3_SECRET_KEY=tu_secret_key
SUPABASE_S3_BUCKET=documentos
SUPABASE_S3_ENDPOINT=https://<project-ref>.supabase.co/storage/v1/s3
SUPABASE_S3_REGION=us-east-1
```

### Crear Bucket en Supabase

1. En Supabase Dashboard → **Storage** → **Create bucket**
2. Nombre: `documentos` (o el valor de `SUPABASE_S3_BUCKET`)
3. **Private bucket** (no público)
4. En **Settings** → **Storage** → **S3 Connection** → **Generate S3 Keys**
4. Copiar **Access Key** y **Secret Key** a `.env`

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `USE_SUPABASE_STORAGE` | Habilita Supabase Storage | `True` / `False` |
| `SUPABASE_S3_ACCESS_KEY` | Access Key de Supabase S3 | `abc123...` |
| `SUPABASE_S3_SECRET_KEY` | Secret Key de Supabase S3 | `xyz789...` |
| `SUPABASE_S3_BUCKET` | Nombre del bucket | `documentos` |
| `SUPABASE_S3_ENDPOINT` | Endpoint S3 de Supabase | `https://abc123.supabase.co/storage/v1/s3` |
| `SUPABASE_S3_REGION` | Región S3 | `us-east-1` |

### Comportamiento

| Entorno | `USE_SUPABASE_STORAGE` | Storage Backend |
|---------|------------------------|-----------------|
| Local (dev) | `False` (default) | `FileSystemStorage` (`MEDIA_ROOT`) |
| Producción | `True` | `S3Storage` (Supabase) |

**Nota**: En local (`USE_SUPABASE_STORAGE=False`), los archivos se guardan en `MEDIA_ROOT` (`./media/`). No se requieren credenciales de Supabase.

## Deploy en Render + Supabase (Paso a Paso)

Esta guía cubre el deploy completo usando **Render Blueprint** (`render.yaml`) y **Supabase** (PostgreSQL + Storage).

---

### 1. Preparar Supabase

#### 1.1 Crear proyecto en Supabase
1. Ir a [supabase.com](https://supabase.com) → **New Project**
2. Organización, nombre del proyecto, contraseña de base de datos, región
3. Esperar a que termine el aprovisionamiento (~2 min)

#### 1.2 Obtener `DATABASE_URL` (Connection Pooling)
1. En Supabase Dashboard → **Settings** → **Database** → **Connection Pooling**
2. **Mode**: Transaction (recomendado para serverless)
3. **Port**: 6543 (pooling) / 5432 (direct)
4. Copiar la **Connection String** (formato URI):
   ```
   postgresql://postgres:<password>@<host>:6543/postgres
   ```
   - Reemplazar `<password>` por la contraseña que definiste al crear el proyecto
   - El host suele ser `db.<project-ref>.supabase.co`

#### 1.3 Crear Bucket en Supabase Storage
1. **Storage** → **Create bucket**
2. Nombre: `documentos` (debe coincidir con `SUPABASE_S3_BUCKET`)
3. **Private bucket** (no público)
4. En **Settings** → **Storage** → **S3 Connection** → **Generate S3 Keys**
5. Copiar **Access Key** y **Secret Key**

---

### 2. Deploy en Render (usando Blueprint `render.yaml`)

#### Opción A: Blueprint (recomendado - Infrastructure as Code)
1. En Render Dashboard → **New** → **Blueprint**
2. Conectar repositorio de GitHub
3. Render detectará `render.yaml` automáticamente
4. Configurar variables de entorno **secretas** (marcadas `sync: false` en el YAML):
   - `SECRET_KEY`: Generar con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `ALLOWED_HOSTS`: `tu-app.onrender.com` (el host que Render asigne)
   - `CSRF_TRUSTED_ORIGINS`: `https://tu-app.onrender.com`
   - `DATABASE_URL`: La URL de Supabase (paso 1.2)
   - `SUPABASE_S3_ACCESS_KEY`: Del paso 1.3
   - `SUPABASE_S3_SECRET_KEY`: Del paso 1.3
   - `SUPABASE_S3_ENDPOINT`: `https://<project-ref>.supabase.co/storage/v1/s3`
5. **Apply** → Render creará el servicio y hará el primer deploy

#### Opción B: Web Service manual
1. **New** → **Web Service** → Conectar repo GitHub
2. **Runtime**: Docker
3. **Dockerfile Path**: `./Dockerfile`
4. **Plan**: Free (o Starter para producción real)
5. Variables de entorno (mismas que arriba)
6. **Create Web Service**

---

### 3. Verificaciones Post-Deploy

1. **Health Check**: `https://tu-app.onrender.com/health/` → debe responder 200 OK
2. **Swagger UI**: `https://tu-app.onrender.com/api/schema/swagger/` → documentación API
3. **Admin**: `https://tu-app.onrender.com/admin/` → crear superusuario si no existe:
   ```bash
   # En Render Shell (Console tab)
   python manage.py createsuperuser
   ```
4. **Static files**: Verificar que CSS/JS cargan en `/admin/` y `/`
5. **Media files**: Subir un documento en admin → verificar que se guarda en Supabase Storage

---

### 4. Variables de Entorno Resumen (Render Dashboard)

| Variable | Valor | Secreto (`sync: false`) |
|----------|-------|------------------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | No |
| `DEBUG` | `False` | No |
| `SECRET_KEY` | `django-insecure-...` (generada) | **Sí** |
| `ALLOWED_HOSTS` | `tu-app.onrender.com` | **Sí** |
| `CSRF_TRUSTED_ORIGINS` | `https://tu-app.onrender.com` | **Sí** |
| `DATABASE_URL` | `postgresql://postgres:xxx@db.xxx.supabase.co:6543/postgres` | **Sí** |
| `USE_SUPABASE_STORAGE` | `True` | No |
| `SUPABASE_S3_ACCESS_KEY` | `xxx` (de Supabase) | **Sí** |
| `SUPABASE_S3_SECRET_KEY` | `xxx` (de Supabase) | **Sí** |
| `SUPABASE_S3_BUCKET` | `documentos` | No |
| `SUPABASE_S3_ENDPOINT` | `https://xxx.supabase.co/storage/v1/s3` | **Sí** |
| `SUPABASE_S3_REGION` | `us-east-1` | No |
| `EMAIL_HOST` | `smtp.gmail.com` (opcional) | No |
| `EMAIL_PORT` | `587` (opcional) | No |
| `EMAIL_USE_TLS` | `True` (opcional) | No |
| `EMAIL_HOST_USER` | `tu-email@gmail.com` (opcional) | **Sí** |
| `EMAIL_HOST_PASSWORD` | `app-password` (opcional) | **Sí** |

---

### 5. Comandos Útiles en Render Shell

```bash
# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Collectstatic (se ejecuta solo en build, pero útil forzar)
python manage.py collectstatic --no-input

# Verificar configuración
python manage.py check --deploy

# Tests
python manage.py test
```

---

### 6. Troubleshooting Común

| Error | Causa | Solución |
|-------|-------|----------|
| `ALLOWED_HOSTS` inválido | Host no incluido | Agregar host exacto en Render Env Vars |
| `CSRF_TRUSTED_ORIGINS` | Falta origen HTTPS | Agregar `https://tu-app.onrender.com` |
| `DATABASE_URL` connection refused | Supabase pausado / pooling | Verificar que proyecto Supabase esté activo; usar puerto 6543 |
| `S3Storage` credentials error | Keys incorrectas | Regenerar S3 Keys en Supabase → Storage → S3 Connection |
| Static files 404 | WhiteNoise no sirviendo | Verificar `STATICFILES_STORAGE` y `collectstatic` ejecutado |
| Health check fails | `/health/` no existe | Agregar vista health en `core/views.py` y URL en `config/urls.py` |

---

## Instalación Local

```bash
# Clonar
git clone <repo-url>
cd centro_salud_api

# Instalar dependencias
uv sync

# Configurar entorno
cp .env.example .env
# Editar .env

# Base de datos (SQLite por defecto)
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Ejecutar
uv run python manage.py runserver
```

### Con Docker (desarrollo)

```bash
# Construir y levantar
docker compose up --build

# El servidor estará en http://localhost:8000
```

## Deploy en Render

### Variables de entorno requeridas en Render Dashboard

```
SECRET_KEY=<generar-con-get_random_secret_key>
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://tu-app.onrender.com
DATABASE_URL=<postgresql-url-de-supabase-o-render>
DJANGO_SETTINGS_MODULE=config.settings.production

# Supabase Storage
USE_SUPABASE_STORAGE=True
SUPABASE_S3_ACCESS_KEY=xxx
SUPABASE_S3_SECRET_KEY=xxx
SUPABASE_S3_BUCKET=documentos
SUPABASE_S3_ENDPOINT=https://xxx.supabase.co/storage/v1/s3
SUPABASE_S3_REGION=us-east-1
```

### Comportamiento del Dockerfile en Render

El `Dockerfile` ejecuta automáticamente al arrancar:
1. `collectstatic --no-input` - recolecta archivos estáticos con WhiteNoise
2. `migrate` - aplica migraciones de base de datos
3. `gunicorn` - sirve la aplicación con 3 workers

WhiteNoise sirve archivos estáticos; los media los sirve Supabase Storage.

## Tests

```bash
# Todos los tests
uv run pytest -q

# Con cobertura
uv run pytest --cov

# Solo tests de storage
uv run pytest documentos/tests/test_storage.py -v
```

## Estructura del Proyecto

```
config/          # Settings, URLs, WSGI/ASGI
core/            # App principal (views, forms, urls)
usuarios/        # Auth, User model
personas/        # Persona, Localidad, etc.
pacientes/       # Paciente, Sala, Area, Diagnostico, Seguimiento
empleados/       # Empleado, Rol, Horario, Asistencia
turnos/          # Turno, Asistencia
tratamientos/    # PlanTratamiento, Objetivo, Actividad, Evolucion
servicios/       # Servicio, TipoServicio
facturacion/     # Factura, Detalle, Pago
inventario/      # Producto, Categoria, MovimientoStock
compras/         # Proveedor, Compra, Gasto
documentos/      # Documento (archivos)
```

## Documentación API

- Swagger UI: `/api/schema/swagger/`
- OpenAPI JSON: `/api/schema/`

## Licencia

Proyecto académico - Prácticas Profesionalizantes II