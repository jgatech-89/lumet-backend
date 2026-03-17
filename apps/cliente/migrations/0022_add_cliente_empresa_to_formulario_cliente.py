# Generated manually: FormularioCliente asociado por ClienteEmpresa (id de producto)

from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


def backfill_cliente_empresa(apps, schema_editor):
    """Asigna cada FormularioCliente existente (cliente_empresa null) al primer ClienteEmpresa del cliente."""
    FormularioCliente = apps.get_model('cliente', 'FormularioCliente')
    ClienteEmpresa = apps.get_model('cliente', 'ClienteEmpresa')
    for fc in FormularioCliente.objects.filter(cliente_empresa__isnull=True):
        ce = ClienteEmpresa.objects.filter(cliente_id=fc.cliente_id, estado='1').order_by('id').first()
        if ce:
            fc.cliente_empresa_id = ce.id
            fc.save(update_fields=['cliente_empresa_id'])


def reverse_backfill(apps, schema_editor):
    pass  # no revertir: dejar los IDs asignados


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0021_alter_cliente_tipo_identificacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulariocliente',
            name='cliente_empresa',
            field=models.ForeignKey(
                blank=True,
                help_text='Si está definido, la respuesta pertenece a este producto; si no, es legacy a nivel cliente.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='respuestas_formulario',
                to='cliente.clienteempresa',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='formulariocliente',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='formulariocliente',
            constraint=models.UniqueConstraint(
                condition=Q(cliente_empresa__isnull=True),
                fields=('cliente', 'nombre_campo'),
                name='unique_formulario_cliente_legacy',
            ),
        ),
        migrations.AddConstraint(
            model_name='formulariocliente',
            constraint=models.UniqueConstraint(
                condition=Q(cliente_empresa__isnull=False),
                fields=('cliente_empresa', 'nombre_campo'),
                name='unique_formulario_cliente_por_producto',
            ),
        ),
        migrations.RunPython(backfill_cliente_empresa, reverse_backfill),
    ]
