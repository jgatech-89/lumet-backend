# Generated migration: remove servicio from Contratista (relaciones vía app relaciones)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contratista', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contratista',
            name='servicio',
        ),
    ]
