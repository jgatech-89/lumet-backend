# Migración de datos: asigna 'pendiente' a clientes con estado_venta vacío o null

from django.db import migrations
from django.db.models import Q


def backfill_estado_venta(apps, schema_editor):
    Cliente = apps.get_model('cliente', 'Cliente')
    Cliente.objects.filter(Q(estado_venta='') | Q(estado_venta__isnull=True)).update(estado_venta='pendiente')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0002_alter_cliente_tipo_cliente'),
    ]

    operations = [
        migrations.RunPython(backfill_estado_venta, noop),
    ]
