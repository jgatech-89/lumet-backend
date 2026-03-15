# Migrar desde cero

Se eliminaron todas las migraciones antiguas. Para tener una base de datos limpia y nuevas migraciones iniciales:

## 1. Resetear la base de datos (PostgreSQL en Docker)

**Opción A – Borrar el volumen de Postgres (recomendado, pierdes todos los datos):**

```bash
# Desde el directorio lumet-backend (donde está docker-compose.yml)
cd /ruta/a/lumet_beta/lumet-backend
docker compose down
docker volume rm lumet_postgres_data_volume
docker compose up -d
```

Al levantar, el backend ejecutará `makemigrations` (generando nuevas `0001_initial.py` por app) y luego `migrate` sobre una base vacía.

**Opción B – Mantener el volumen y borrar solo tablas (avanzado):**

Si quieres conservar el volumen pero dejar la BD como recién creada, conecta al contenedor de Postgres y borra la base y créala de nuevo, o ejecuta un script que elimine todas las tablas. No es necesario si estás en desarrollo y puedes usar la opción A.

## 2. Si no usas Docker

```bash
# Eliminar la base de datos (PostgreSQL local)
psql -U postgres -c "DROP DATABASE IF EXISTS lumet_db;"
psql -U postgres -c "CREATE DATABASE lumet_db OWNER lumet_user;"

# Crear y aplicar migraciones
cd lumet-backend
python manage.py makemigrations
python manage.py migrate
```

## Resumen

| Paso | Acción |
|------|--------|
| 1 | Migraciones viejas ya eliminadas (solo quedan `__init__.py` en cada app). |
| 2 | Resetear BD: `docker compose down` + `docker volume rm lumet_postgres_data_volume` + `docker compose up -d`. |
| 3 | El backend al arrancar hace `makemigrations` y `migrate`; la BD queda con el esquema actual. |

Si el `docker-compose` está en la raíz de `lumet_beta` y no dentro de `lumet-backend`, ajusta la ruta desde la que ejecutas `docker compose`.
