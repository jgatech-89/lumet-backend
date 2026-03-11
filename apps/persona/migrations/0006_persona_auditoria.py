# Migración: campos de auditoría en Persona

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0005_vendedor_auditoria_y_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='persona',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='personas_creadas', to='persona.Persona', verbose_name='Creado por'),
        ),
        migrations.AddField(
            model_name='persona',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='personas_actualizadas', to='persona.Persona', verbose_name='Actualizado por'),
        ),
        migrations.AddField(
            model_name='persona',
            name='deleted_at',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='persona',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='personas_eliminadas', to='persona.Persona', verbose_name='Eliminado por'),
        ),
    ]
