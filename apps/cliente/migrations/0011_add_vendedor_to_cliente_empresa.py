# Generated manually - add vendedor to ClienteEmpresa (relaciona vendedor con producto vendido)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0010_add_direccion'),
        ('persona', '0004_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='clienteempresa',
            name='vendedor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cliente_empresas',
                to='persona.vendedor',
                verbose_name='Vendedor del producto',
            ),
        ),
    ]
