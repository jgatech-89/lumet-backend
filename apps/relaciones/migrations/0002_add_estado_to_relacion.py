# Migración: agregar campo estado a Relacion (activar/desactivar sin borrar)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='relacion',
            name='estado',
            field=models.CharField(
                choices=[('1', 'Activo'), ('0', 'Inactivo')],
                default='1',
                help_text='1 = activa, 0 = inactiva (no se elimina físicamente)',
                max_length=20,
                verbose_name='Estado',
            ),
        ),
    ]
