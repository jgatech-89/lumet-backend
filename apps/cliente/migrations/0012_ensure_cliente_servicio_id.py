# Asegura que la tabla cliente_cliente tenga la columna servicio_id (puede faltar por historial de migraciones distinto)

from django.db import migrations


def add_servicio_id_if_missing(apps, schema_editor):
    """Añade servicio_id a cliente_cliente si no existe (compatible con PostgreSQL y SQLite)."""
    from django.db import connection
    with connection.cursor() as cursor:
        table = 'cliente_cliente'
        column = 'servicio_id'
        if connection.vendor == 'postgresql':
            cursor.execute(
                f"""
                SELECT 1 FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table, column],
            )
            if not cursor.fetchone():
                cursor.execute(
                    f'ALTER TABLE {table} ADD COLUMN {column} integer NULL;'
                )
        elif connection.vendor == 'sqlite':
            cursor.execute(
                f"PRAGMA table_info({table})"
            )
            columns = [row[1] for row in cursor.fetchall()]
            if column not in columns:
                cursor.execute(
                    f'ALTER TABLE {table} ADD COLUMN {column} integer NULL;'
                )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0011_add_vendedor_to_cliente_empresa'),
    ]

    operations = [
        migrations.RunPython(add_servicio_id_if_missing, noop),
    ]
