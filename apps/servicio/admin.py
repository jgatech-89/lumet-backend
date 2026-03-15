from django.contrib import admin
from .models import Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'estado',
        'estado_servicio',
        'usuario_registra',
        'fecha_registro',
        'usuario_edita',
        'fecha_edita',
        'usuario_elimina',
        'fecha_elimina',
    ]
    list_filter = ['estado', 'estado_servicio']
    search_fields = ['nombre']
    readonly_fields = [
        'usuario_registra',
        'usuario_edita',
        'usuario_elimina',
        'fecha_registro',
        'fecha_edita',
        'fecha_elimina',
    ]
    ordering = ['nombre']
