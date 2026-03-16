# Generated manually for Campo.depende_de (self FK)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0004_alter_campo_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='campo',
            name='depende_de',
            field=models.ForeignKey(
                blank=True,
                help_text='Campo del que depende este (ej. Contratista depende de Servicio). Misma sección.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campos_dependientes',
                to='formularios.campo',
            ),
        ),
    ]
