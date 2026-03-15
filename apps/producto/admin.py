from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'estado',
        'estado_producto',
        'usuario_registra',
        'fecha_registra',
        'updated_by',
        'updated_at',
        'usuario_elimina',
        'fecha_elimina',
    ]
    list_filter = ['estado', 'estado_producto']
    search_fields = ['nombre']
    readonly_fields = [
        'usuario_registra',
        'fecha_registra',
        'updated_by',
        'updated_at',
        'usuario_elimina',
        'fecha_elimina',
    ]
    ordering = ['nombre']
