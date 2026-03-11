# Renombrar nombre -> nombre_completo en Vendedor

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0006_persona_auditoria'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendedor',
            old_name='nombre',
            new_name='nombre_completo',
        ),
    ]
