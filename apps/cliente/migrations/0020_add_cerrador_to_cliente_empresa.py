# Add cerrador to ClienteEmpresa (same as vendedor - FK to Vendedor)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0019_remove_cups_add_documentos'),
        ('persona', '0004_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='clienteempresa',
            name='cerrador',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cliente_empresas_cerrador',
                to='persona.vendedor',
                verbose_name='Cerrador',
            ),
        ),
    ]
