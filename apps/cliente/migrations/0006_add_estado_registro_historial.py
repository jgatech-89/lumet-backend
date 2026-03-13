# Estandarizar auditoría: estado_registro en HistorialEstadoVenta

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0005_historial_estado_venta_and_remove_cliente_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='historialestadoventa',
            name='estado_registro',
            field=models.CharField(
                choices=[('1', 'Activo'), ('0', 'Inactivo')],
                default='1',
                help_text='1=activo, 0=eliminado',
                max_length=20,
            ),
        ),
    ]
