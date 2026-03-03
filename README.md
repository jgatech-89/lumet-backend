# Lumet Backend

Backend Django REST Framework con autenticación JWT y CRUD de productos. Configurado para desarrollo con Docker.

## Estructura del proyecto

```
project-root/
├── config/          # Configuración Django (settings, urls, wsgi, asgi)
├── apps/
│   └── core/        # App principal (Product, API)
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
| Admin | http://localhost:8000/admin/ |
| Obtener JWT (POST username, password) | http://localhost:8000/api/token/ |
| Refrescar JWT (POST refresh) | http://localhost:8000/api/token/refresh/ |
| CRUD Productos (requiere JWT) | http://localhost:8000/api/products/ |

## Contenedores y volumen

- **lumet_backend_container**: aplicación Django
- **lumet_postgres_container**: PostgreSQL 15
- **lumet_postgres_data_volume**: datos de PostgreSQL

## Crear superusuario (para admin y JWT)

```bash
docker compose exec lumet_backend_container python manage.py createsuperuser
```

Luego obtén el token en `POST /api/token/` con `username` y `password` del superusuario.
