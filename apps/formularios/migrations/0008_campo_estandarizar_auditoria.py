# Estandarizar auditoría: usuario_registra, usuario_elimina, fecha_registra, fecha_elimina

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0007_add_producto_to_campo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Campo: renombrar campos
        migrations.RenameField(
            model_name='campo',
            old_name='created_at',
            new_name='fecha_registra',
        ),
        migrations.RenameField(
            model_name='campo',
            old_name='created_by',
            new_name='usuario_registra',
        ),
        migrations.RenameField(
            model_name='campo',
            old_name='deleted_at',
            new_name='fecha_elimina',
        ),
        migrations.RenameField(
            model_name='campo',
            old_name='deleted_by',
            new_name='usuario_elimina',
        ),
        migrations.AlterField(
            model_name='campo',
            name='usuario_registra',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campos_formulario_registrados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuario registra',
            ),
        ),
        migrations.AlterField(
            model_name='campo',
            name='usuario_elimina',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campos_formulario_eliminados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuario elimina',
            ),
        ),
        # CampoOpcion: añadir campos de auditoría
        migrations.AddField(
            model_name='campoopcion',
            name='estado',
            field=models.CharField(
                choices=[('1', 'Activo'), ('0', 'Inactivo')],
                default='1',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='campoopcion',
            name='fecha_registra',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.AddField(
            model_name='campoopcion',
            name='usuario_registra',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campo_opciones_registradas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuario registra',
            ),
        ),
        migrations.AddField(
            model_name='campoopcion',
            name='fecha_elimina',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='campoopcion',
            name='usuario_elimina',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campo_opciones_eliminadas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuario elimina',
            ),
        ),
    ]
