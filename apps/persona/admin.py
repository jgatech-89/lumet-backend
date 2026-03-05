from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Persona

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
                'updated_at',
            ),
        }),
    )
    readonly_fields = ['updated_at']
