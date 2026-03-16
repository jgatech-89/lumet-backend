# Generated manually for entity_select support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campo',
            name='entidad',
            field=models.CharField(
                blank=True,
                help_text='Solo cuando tipo=entity_select: servicio, contratista, producto o vendedor.',
                max_length=50,
                null=True,
            ),
        ),
    ]
