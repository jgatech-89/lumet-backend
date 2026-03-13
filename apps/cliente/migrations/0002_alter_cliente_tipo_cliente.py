# Generated manually - tipo_cliente debe aceptar valores dinámicos de la tabla campos (más largos que 2 chars)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='tipo_cliente',
            field=models.CharField(max_length=50, default='2'),
        ),
    ]
