# Estandarizar auditoría: usuario_registra, usuario_elimina, fecha_registra, fecha_elimina

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0009_vendedor_estado_vendedor'),
    ]

    operations = [
        # Eliminar constraint anterior (usa deleted_at)
        migrations.RemoveConstraint(
            model_name='vendedor',
            name='vendedor_tipo_num_id_uniq_activo',
        ),
        # Renombrar campos
        migrations.RenameField(
            model_name='vendedor',
            old_name='created_at',
            new_name='fecha_registra',
        ),
        migrations.RenameField(
            model_name='vendedor',
            old_name='created_by',
            new_name='usuario_registra',
        ),
        migrations.RenameField(
            model_name='vendedor',
            old_name='deleted_at',
            new_name='fecha_elimina',
        ),
        migrations.RenameField(
            model_name='vendedor',
            old_name='deleted_by',
            new_name='usuario_elimina',
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='usuario_registra',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='vendedores_registrados',
                to='persona.persona',
                verbose_name='Usuario registra',
            ),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='usuario_elimina',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='vendedores_eliminados',
                to='persona.persona',
                verbose_name='Usuario elimina',
            ),
        ),
        # Recrear constraint con fecha_elimina
        migrations.AddConstraint(
            model_name='vendedor',
            constraint=models.UniqueConstraint(
                condition=Q(fecha_elimina__isnull=True),
                fields=('tipo_identificacion', 'numero_identificacion'),
                name='vendedor_tipo_num_id_uniq_activo',
            ),
        ),
    ]
