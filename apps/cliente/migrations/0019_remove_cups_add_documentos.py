# Generated manually - Remove CUPS, add documento_dni and documento_factura

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0018_alter_cliente_correo_electronico_o_carta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='cups',
        ),
        migrations.AddField(
            model_name='cliente',
            name='documento_dni',
            field=models.FileField(blank=True, null=True, upload_to='clientes/documentos/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='documento_factura',
            field=models.FileField(blank=True, null=True, upload_to='clientes/documentos/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='creado_por_carga_masiva',
            field=models.BooleanField(default=False),
        ),
    ]
