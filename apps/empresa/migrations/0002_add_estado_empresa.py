# Generated manually - add estado_empresa to Empresa (like estado_vendedor in Vendedor)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='estado_empresa',
            field=models.CharField(
                choices=[('1', 'Activo'), ('0', 'Inactivo')],
                default='1',
                max_length=20,
                verbose_name='Estado empresa',
            ),
        ),
    ]
