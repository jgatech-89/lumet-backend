# Migración: auditoría completa y campo estado en Vendedor

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0004_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendedor',
            name='estado',
            field=models.CharField(choices=[('1', 'Activo'), ('0', 'Inactivo')], default='1', max_length=20),
        ),
        migrations.AddField(
            model_name='vendedor',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='vendedores_creados', to='persona.Persona', verbose_name='Creado por'),
        ),
        migrations.AddField(
            model_name='vendedor',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='vendedores_actualizados', to='persona.Persona', verbose_name='Actualizado por'),
        ),
        migrations.AddField(
            model_name='vendedor',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='vendedores_eliminados', to='persona.Persona', verbose_name='Eliminado por'),
        ),
    ]
