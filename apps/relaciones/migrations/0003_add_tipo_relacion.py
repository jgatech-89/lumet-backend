# Migración: agregar campo tipo_relacion a Relacion (estructura vs contexto_campo)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relaciones', '0002_add_estado_to_relacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='relacion',
            name='tipo_relacion',
            field=models.CharField(
                choices=[('estructura', 'Relación estructural'), ('contexto_campo', 'Campo aplica a contexto')],
                default='estructura',
                help_text='estructura: dependencias entre entidades; contexto_campo: cuándo un campo aplica en el formulario.',
                max_length=30,
                verbose_name='Tipo de relación',
            ),
        ),
    ]
