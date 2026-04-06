# Choices alineados con apps.core.choices.TIPO_IDENTIFICACION (CC, CE, etc.)

from django.db import migrations, models


_TIPO_IDENTIFICACION = [
    ('CC', 'CÉDULA DE CIUDADANÍA'),
    ('CE', 'CÉDULA DE EXTRANJERÍA'),
    ('NIT', 'NÚMERO DE IDENTIFICACIÓN TRIBUTARIO'),
    ('PAS', 'PASAPORTE'),
    ('TI', 'TARJETA DE IDENTIDAD'),
    ('PPT', 'PERMISO PROVISIONAL DE TRABAJO'),
    ('DNI', 'DOCUMENTO NACIONAL DE IDENTIDAD'),
    ('NIE', 'NÚMERO DE IDENTIFICACIÓN DE EXTRANJERO'),
    ('CIF', 'CÓDIGO DE IDENTIFICACIÓN FISCAL'),
    ('OTRO', 'OTRO DOCUMENTO'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0022_add_cliente_empresa_to_formulario_cliente'),
        ('persona', '0014_alter_tipo_identificacion_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='tipo_identificacion',
            field=models.CharField(blank=True, choices=_TIPO_IDENTIFICACION, max_length=10),
        ),
    ]
