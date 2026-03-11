from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Persona, Vendedor

try:
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
    admin.site.unregister(BlacklistedToken)
    admin.site.unregister(OutstandingToken)
except Exception:
    pass


@admin.register(Persona)
class PersonaAdmin(BaseUserAdmin):
    list_display = [
        'username', 'primer_nombre', 'primer_apellido', 'correo', 'correo_auth',
        'identificacion', 'perfil', 'estado', 'verificado', 'is_active',
        'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by',
    ]
    list_filter = ['perfil', 'estado', 'verificado', 'is_active', 'tipo_identificacion']
    search_fields = [
        'username', 'primer_nombre', 'primer_apellido', 'correo', 'correo_auth',
        'segundo_nombre', 'segundo_apellido', 'identificacion',
    ]
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Persona', {
            'fields': (
                'tipo_identificacion', 'identificacion',
                'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
                'correo', 'correo_auth',
                'telefono', 'perfil', 'estado', 'verificado', 'codigo_verificado',
                'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by',
            ),
        }),
    )
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_completo', 'tipo_identificacion', 'numero_identificacion', 'estado',
        'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by',
    ]
    list_filter = ['tipo_identificacion', 'estado']
    search_fields = ['nombre_completo', 'numero_identificacion']
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return Vendedor.objects.all()
