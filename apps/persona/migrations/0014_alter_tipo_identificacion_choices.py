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
]


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0013_alter_persona_tipo_identificacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='tipo_identificacion',
            field=models.CharField(choices=_TIPO_IDENTIFICACION, max_length=10),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='tipo_identificacion',
            field=models.CharField(blank=True, choices=_TIPO_IDENTIFICACION, max_length=10),
        ),
    ]
