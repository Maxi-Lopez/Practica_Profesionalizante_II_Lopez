# Ingenieria-TP-Final-Lopez

# Centro de Día Proyectar - API

API REST para la gestión integral del Centro de Día Proyectar.

## Tecnologías

- **Backend**: Django 6.1 + Django REST Framework 3.18
- **Base de datos**: PostgreSQL (Supabase) / SQLite (desarrollo)
- **Autenticación**: JWT (SimpleJWT)
- **Documentación**: drf-spectacular (OpenAPI/Swagger)
- **Tests**: pytest + model-bakery
- **Storage**: Supabase Storage (S3 compatible) para producción / FileSystem (local)

## Configuración de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### Variables Principales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `USE_SQLITE` | Usar SQLite en lugar de PostgreSQL | `True` (dev) |
| `SECRET_KEY` | Clave secreta de Django | (requerida) |
| `DEBUG` | Modo debug | `True` (dev) |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

### Base de Datos (PostgreSQL)

```env
USE_SQLITE=False
DB_NAME=centro_salud_db
DB_USER=centro_salud_user
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432
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

### Despliegue en Render

En Render Dashboard → **Environment Variables**, agregar las 5 variables de Supabase Storage:

```
USE_SUPABASE_STORAGE=True
SUPABASE_S3_ACCESS_KEY=xxx
SUPABASE_S3_SECRET_KEY=xxx
SUPABASE_S3_BUCKET=documentos
SUPABASE_S3_ENDPOINT=https://xxx.supabase.co/storage/v1/s3
SUPABASE_S3_REGION=us-east-1
```

WhiteNoise sirve archivos estáticos; los media los sirve Supabase Storage.

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
config/          # Settings, URLs, WSGI
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