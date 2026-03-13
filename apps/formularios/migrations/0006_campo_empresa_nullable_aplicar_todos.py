# Generated manually - Campos para todas las empresas y todos los servicios

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0005_campo_empresa_required_servicio_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campo',
            name='empresa',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='campos_formulario',
                to='empresa.empresa',
                help_text='Si es null, aplica a todas las empresas.',
            ),
        ),
    ]
