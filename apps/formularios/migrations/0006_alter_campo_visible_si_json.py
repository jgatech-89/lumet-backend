# Migración: cambiar Campo.visible_si de CharField a JSONField
# Formato esperado: {"campo": "nombre_campo", "valor": "valor_esperado"}

import json
from django.db import migrations, models


def migrar_visible_si_a_json(apps, schema_editor):
    Campo = apps.get_model('formularios', 'Campo')
    for c in Campo.objects.all():
        old = getattr(c, 'visible_si_old', None) or ''
        if isinstance(old, str) and old.strip():
            try:
                parsed = json.loads(old)
                if isinstance(parsed, dict) and 'campo' in parsed and 'valor' in parsed:
                    c.visible_si = parsed
                else:
                    c.visible_si = None
            except (json.JSONDecodeError, TypeError):
                c.visible_si = None
        else:
            c.visible_si = None
        c.save(update_fields=['visible_si'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0005_add_campo_depende_de'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campo',
            old_name='visible_si',
            new_name='visible_si_old',
        ),
        migrations.AddField(
            model_name='campo',
            name='visible_si',
            field=models.JSONField(
                blank=True,
                help_text='Condición que determina cuándo se muestra el campo. Ej: {"campo": "tipo_cliente", "valor": "empresa"}',
                null=True,
                verbose_name='Condición de visibilidad',
            ),
        ),
        migrations.RunPython(migrar_visible_si_a_json, noop),
        migrations.RemoveField(
            model_name='campo',
            name='visible_si_old',
        ),
    ]
