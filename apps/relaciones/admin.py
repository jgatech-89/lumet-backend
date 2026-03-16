"""
Registro del modelo Relacion en Django Admin.
"""
from django.contrib import admin
from .models import Relacion


@admin.register(Relacion)
class RelacionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'origen_tipo',
        'origen_id',
        'destino_tipo',
        'destino_id',
        'estado',
        'created_at',
    ]
    list_filter = ['estado', 'origen_tipo', 'destino_tipo']
    search_fields = ['origen_tipo', 'destino_tipo']
    ordering = ['origen_tipo', 'origen_id', 'destino_tipo', 'destino_id']
