# Asegura que cliente_clienteempresa tenga empresa_id, servicio_id y vendedor_id si faltan

from django.db import migrations


def ensure_columns(apps, schema_editor):
    """Añade columnas faltantes a cliente_clienteempresa (PostgreSQL)."""
    from django.db import connection
    table = 'cliente_clienteempresa'
    columns_to_add = [
        ('empresa_id', 'integer'),
        ('servicio_id', 'integer'),
        ('vendedor_id', 'integer'),
    ]
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            for col_name, col_type in columns_to_add:
                cursor.execute(
                    """
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s
                    """,
                    [table, col_name],
                )
                if not cursor.fetchone():
                    cursor.execute(
                        f'ALTER TABLE {table} ADD COLUMN {col_name} {col_type} NULL;'
                    )
        elif connection.vendor == 'sqlite':
            cursor.execute(f'PRAGMA table_info({table})')
            existing = [row[1] for row in cursor.fetchall()]
            for col_name, col_type in columns_to_add:
                if col_name not in existing:
                    cursor.execute(
                        f'ALTER TABLE {table} ADD COLUMN {col_name} {col_type} NULL;'
                    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0012_ensure_cliente_servicio_id'),
    ]

    operations = [
        migrations.RunPython(ensure_columns, noop),
    ]
