from django.contrib import admin
from .models import Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'empresa',
        'estado',
        'estado_servicio',
        'usuario_registra',
        'fecha_registro',
    ]
    list_filter = ['estado', 'estado_servicio', 'empresa']
    search_fields = ['nombre', 'empresa__nombre']
    list_select_related = ['empresa', 'usuario_registra', 'usuario_edita', 'usuario_elimina']
    readonly_fields = [
        'fecha_registro',
        'fecha_edita',
        'fecha_elimina',
        'usuario_registra',
        'usuario_edita',
        'usuario_elimina',
    ]
    ordering = ['nombre']

    fieldsets = (
        (None, {
            'fields': ('nombre', 'estado', 'estado_servicio', 'empresa'),
        }),
        ('Auditoría', {
            'fields': (
                'usuario_registra',
                'usuario_edita',
                'usuario_elimina',
                'fecha_registro',
                'fecha_edita',
                'fecha_elimina',
            ),
            'classes': ('collapse',),
        }),
    )
