# Generated manually - Cambio lógico: empresa obligatoria, servicio opcional (aplicar a todos los servicios)

from django.db import migrations, models
import django.db.models.deletion


def asignar_empresa_default(apps, schema_editor):
    """Asignar primera empresa activa a campos con empresa null (legacy)."""
    Campo = apps.get_model('formularios', 'Campo')
    Empresa = apps.get_model('empresa', 'Empresa')
    primera = Empresa.objects.filter(estado='1').order_by('id').first()
    if primera:
        Campo.objects.filter(empresa__isnull=True).update(empresa=primera)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0004_campo_empresa_nullable'),
    ]

    operations = [
        migrations.RunPython(asignar_empresa_default, noop),
        migrations.AlterField(
            model_name='campo',
            name='empresa',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='campos_formulario',
                to='empresa.empresa',
                help_text='Empresa a la que aplica el campo.',
            ),
        ),
        migrations.AlterField(
            model_name='campo',
            name='servicio',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='campos_formulario',
                to='servicio.servicio',
                help_text='Si es null, aplica a todos los servicios de la empresa.',
            ),
        ),
    ]
