from django.contrib import admin
from .models import Campo, CampoOpcion


class CampoOpcionInline(admin.TabularInline):
    model = CampoOpcion
    extra = 0
    ordering = ['orden']


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'empresa', 'servicio', 'orden', 'requerido', 'activo', 'estado']
    list_filter = ['tipo', 'activo', 'estado', 'empresa', 'servicio']
    search_fields = ['nombre', 'placeholder']
    ordering = ['empresa', 'servicio', 'orden']
    raw_id_fields = ['empresa', 'servicio', 'usuario_registra', 'updated_by', 'usuario_elimina']
    readonly_fields = ['fecha_registra', 'updated_at', 'fecha_elimina']
    inlines = [CampoOpcionInline]


@admin.register(CampoOpcion)
class CampoOpcionAdmin(admin.ModelAdmin):
    list_display = ['campo', 'label', 'value', 'orden', 'activo']
    list_filter = ['activo', 'campo']
    ordering = ['campo', 'orden']
