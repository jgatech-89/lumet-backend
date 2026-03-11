from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'estado',
        'estado_empresa',
        'usuario_registra',
        'fecha_registro',
        'usuario_edita',
        'fecha_edita',
        'usuario_elimina',
        'fecha_elimina',
    ]
    list_filter = ['estado', 'estado_empresa']
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
