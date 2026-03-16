# Generated manually - Sección del formulario para campos dinámicos

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0009_alter_campoopcion_fecha_registra'),
    ]

    operations = [
        migrations.AddField(
            model_name='campo',
            name='seccion',
            field=models.CharField(
                choices=[
                    ('cliente', 'Cliente'),
                    ('datos_base', 'Datos base'),
                    ('campos_formulario', 'Campos del formulario'),
                    ('vendedor', 'Vendedor'),
                ],
                default='campos_formulario',
                help_text='Sección del formulario a la que pertenece el campo.',
                max_length=30,
            ),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='campo',
            options={'ordering': ['seccion', 'orden', 'id'], 'verbose_name': 'Campo', 'verbose_name_plural': 'Campos'},
        ),
    ]
