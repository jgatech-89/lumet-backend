# Generated manually for add_vendedor

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0003_alter_persona_correo_auth_alter_persona_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('tipo_identificacion', models.CharField(blank=True, choices=[('CC', 'Cédula de ciudadanía'), ('CE', 'Cédula de extranjería'), ('NIT', 'NIT'), ('PAS', 'Pasaporte'), ('TI', 'Tarjeta de identidad'), ('OTRO', 'Otro')], max_length=10)),
                ('numero_identificacion', models.CharField(db_index=True, max_length=50)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Vendedor',
                'verbose_name_plural': 'Vendedores',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='vendedor',
            constraint=models.UniqueConstraint(condition=Q(deleted_at__isnull=True), fields=('tipo_identificacion', 'numero_identificacion'), name='vendedor_tipo_num_id_uniq_activo'),
        ),
    ]
