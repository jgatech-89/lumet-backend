# Migración: Crear HistorialEstadoVenta, migrar datos, eliminar tipo_cliente, estado_venta, vendedor de Cliente

from django.db import migrations, models
import django.db.models.deletion


def migrar_datos(apps, schema_editor):
    Cliente = apps.get_model('cliente', 'Cliente')
    HistorialEstadoVenta = apps.get_model('cliente', 'HistorialEstadoVenta')
    FormularioCliente = apps.get_model('cliente', 'FormularioCliente')
    Persona = apps.get_model('persona', 'Persona')

    for c in Cliente.objects.all():
        # Migrar estado_venta a HistorialEstadoVenta
        ev = (getattr(c, 'estado_venta', None) or '').strip() or 'pendiente'
        HistorialEstadoVenta.objects.create(
            cliente=c,
            estado=ev,
            activo=True,
            usuario_registra=c.usuario_registra,
        )
        # Migrar tipo_cliente y vendedor a FormularioCliente
        tc = getattr(c, 'tipo_cliente', None) or ''
        if tc:
            FormularioCliente.objects.get_or_create(
                cliente=c,
                nombre_campo='tipo_cliente',
                defaults={'respuesta_campo': str(tc), 'usuario_registra': c.usuario_registra}
            )
        vendedor = getattr(c, 'vendedor_id', None)
        if vendedor:
            FormularioCliente.objects.get_or_create(
                cliente=c,
                nombre_campo='vendedor',
                defaults={'respuesta_campo': str(vendedor), 'usuario_registra': c.usuario_registra}
            )
        ev_val = getattr(c, 'estado_venta', None) or ''
        if ev_val:
            FormularioCliente.objects.get_or_create(
                cliente=c,
                nombre_campo='estado_venta',
                defaults={'respuesta_campo': str(ev_val), 'usuario_registra': c.usuario_registra}
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0009_vendedor_estado_vendedor'),
        ('cliente', '0004_add_producto_to_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialEstadoVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=50)),
                ('activo', models.BooleanField(default=True)),
                ('fecha_registra', models.DateTimeField(auto_now_add=True)),
                ('fecha_elimina', models.DateTimeField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_estados_venta', to='cliente.cliente')),
                ('usuario_elimina', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='historial_estado_venta_eliminados', to='persona.persona')),
                ('usuario_registra', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='historial_estado_venta_registrados', to='persona.persona')),
            ],
            options={
                'verbose_name': 'Historial estado de venta',
                'verbose_name_plural': 'Historial estados de venta',
                'ordering': ['-fecha_registra'],
            },
        ),
        migrations.RunPython(migrar_datos, noop),
        migrations.RemoveField(model_name='cliente', name='tipo_cliente'),
        migrations.RemoveField(model_name='cliente', name='estado_venta'),
        migrations.RemoveField(model_name='cliente', name='vendedor'),
    ]
