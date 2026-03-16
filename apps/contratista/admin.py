from django.contrib import admin
from .models import Contratista


@admin.register(Contratista)
class ContratistaAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'estado',
        'estado_contratista',
        'usuario_registra',
        'fecha_registro',
    ]
    list_filter = ['estado', 'estado_contratista']
    search_fields = ['nombre']
    list_select_related = ['usuario_registra', 'usuario_edita', 'usuario_elimina']
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
            'fields': ('nombre', 'estado', 'estado_contratista'),
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
