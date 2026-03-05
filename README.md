# Lumet Backend

Backend Django REST Framework con autenticación JWT y app Persona. Configurado para desarrollo con Docker.

## Estructura del proyecto

```
project-root/
├── config/          # Configuración Django (settings, urls, wsgi, asgi)
├── apps/
│   └── persona/     # App Persona (modelo, API, choices)
├── manage.py
└── ...
```

## Requisitos

- Docker y Docker Compose

## Comandos para ejecutar

```bash
docker compose build
docker compose up
```

## URLs disponibles

| Recurso | URL |
|--------|-----|
| Backend | http://localhost:8000 |
| **Documentación API (Swagger)** | http://localhost:8000/api/docs/ |
| **Documentación API (ReDoc)** | http://localhost:8000/api/docs/redoc/ |
| Admin (solo si `DEBUG=1`) | http://localhost:8000/admin/ |
| **Login** (POST correo, password) | http://localhost:8000/auth/login |
| **Verificar código** (POST correo, codigo) → JWT | http://localhost:8000/auth/verificar-codigo |
| **Refresh token** (POST refresh) | http://localhost:8000/auth/refresh |
| **Usuario actual** (GET, requiere JWT) | http://localhost:8000/auth/me |
| **Reenviar código** (POST correo) | http://localhost:8000/auth/resend-code |
| CRUD Personas (requiere JWT) | http://localhost:8000/api/personas/ |

### Documentación OpenAPI (drf-spectacular)

Tras `docker compose build` y `docker compose up`:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/docs/redoc/
- **Schema JSON:** http://localhost:8000/api/docs/schema/

### Flujo de login (con código por correo)

1. **POST /auth/login** con `{"correo": "...", "password": "..."}`  
   → Se valida; si es correcto se envía un código de 6 dígitos al correo (respuesta siempre genérica).
2. **POST /auth/verificar-codigo** con `{"correo": "...", "codigo": "123456"}`  
   → Si el código es correcto, se devuelve `{"access_token": "...", "refresh_token": "..."}`.
3. Usar el `access_token` en el header: `Authorization: Bearer <access_token>` para `/auth/me` y `/api/personas/`.

En desarrollo el correo se imprime en la consola (backend). En producción hay que configurar SMTP en `.env`.

## Contenedores y volumen

- **lumet_backend** (contenedor: lumet_backend_container): aplicación Django
- **lumet_postgres** (contenedor: lumet_postgres_container): PostgreSQL 15
- **lumet_postgres_data_volume**: datos de PostgreSQL

Para `docker compose exec` usa el **nombre del servicio** (ej. `lumet_postgres`, `lumet_backend`), no el nombre del contenedor.

## Crear superusuario (para admin y JWT)

```bash
docker compose exec lumet_backend python manage.py createsuperuser
```

Para login en la app usa el flujo de dos pasos: `POST /api/auth/login/` (correo + contraseña) y luego `POST /api/auth/verify-code/` (correo + código). El admin de Django **solo está habilitado cuando `DEBUG=1`**; en producción (`DEBUG=0`) la ruta `/admin/` devuelve 403.

## Reset de base de datos (si hay migraciones inconsistentes)

Si ves `InconsistentMigrationHistory` o necesitas empezar con la BD limpia:

```bash
# 1. Detener backend (y frontend) para que suelten la conexión a la BD
docker compose stop lumet_backend lumet_frontend

# 2. Borrar y recrear la base de datos
docker compose exec lumet_postgres psql -U lumet_user -d postgres -c "DROP DATABASE IF EXISTS lumet_db;"
docker compose exec lumet_postgres psql -U lumet_user -d postgres -c "CREATE DATABASE lumet_db;"

# 3. Aplicar migraciones
docker compose run --rm lumet_backend python manage.py migrate

# 4. Volver a levantar los servicios
docker compose start lumet_backend lumet_frontend
```

Luego crea de nuevo el superusuario con `createsuperuser`.
