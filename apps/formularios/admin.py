from django.contrib import admin
from .models import Campo, CampoOpcion


class CampoOpcionInline(admin.TabularInline):
    model = CampoOpcion
    extra = 0
    ordering = ['orden']


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'servicio', 'contratista', 'orden', 'requerido', 'activo', 'estado']
    list_filter = ['tipo', 'activo', 'estado', 'servicio', 'contratista']
    search_fields = ['nombre', 'placeholder']
    ordering = ['servicio', 'contratista', 'orden']
    raw_id_fields = ['servicio', 'contratista', 'usuario_registra', 'updated_by', 'usuario_elimina']
    readonly_fields = ['fecha_registra', 'updated_at', 'fecha_elimina']
    inlines = [CampoOpcionInline]


@admin.register(CampoOpcion)
class CampoOpcionAdmin(admin.ModelAdmin):
    list_display = ['campo', 'label', 'value', 'orden', 'activo']
    list_filter = ['activo', 'campo']
    ordering = ['campo', 'orden']
