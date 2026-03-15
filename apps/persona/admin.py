from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Persona, Vendedor
from apps.cliente.models import ClienteEmpresa

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


class ClienteEmpresaVendedorInline(admin.TabularInline):
    """Muestra los productos (ClienteEmpresa) asociados a este vendedor."""
    model = ClienteEmpresa
    fk_name = 'vendedor'
    extra = 0
    readonly_fields = ['cliente', 'tipo_cliente', 'servicio', 'contratista', 'producto', 'estado', 'fecha_registra']
    can_delete = False
    max_num = 0
    show_change_link = True
    verbose_name = 'Producto vendido'
    verbose_name_plural = 'Productos vendidos por este vendedor'


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_completo', 'tipo_identificacion', 'numero_identificacion', 'estado',
        'fecha_registra', 'usuario_registra', 'updated_at', 'updated_by', 'fecha_elimina', 'usuario_elimina',
    ]
    list_filter = ['tipo_identificacion', 'estado']
    search_fields = ['nombre_completo', 'numero_identificacion']
    readonly_fields = ['fecha_registra', 'usuario_registra', 'updated_at', 'updated_by', 'fecha_elimina', 'usuario_elimina']
    ordering = ['-fecha_registra']
    inlines = [ClienteEmpresaVendedorInline]

    def get_queryset(self, request):
        return Vendedor.objects.all()
