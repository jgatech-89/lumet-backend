# Generated manually for estado_vendedor

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0008_alter_persona_tipo_identificacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendedor',
            name='estado_vendedor',
            field=models.CharField(
                choices=[('1', 'Activo'), ('0', 'Inactivo')],
                default='1',
                max_length=20,
                verbose_name='Estado vendedor',
            ),
        ),
    ]
