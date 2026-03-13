from django.contrib import admin
from .models import Cliente, FormularioCliente, HistorialEstadoVenta, ClienteEmpresa


class FormularioClienteInline(admin.TabularInline):
    model = FormularioCliente
    extra = 0
    readonly_fields = ['nombre_campo', 'respuesta_campo', 'fecha_registra']
    can_delete = True


class HistorialEstadoVentaInline(admin.TabularInline):
    model = HistorialEstadoVenta
    extra = 0
    readonly_fields = ['estado', 'estado_registro', 'activo', 'fecha_registra']
    can_delete = True


class ClienteEmpresaInline(admin.TabularInline):
    model = ClienteEmpresa
    extra = 0
    readonly_fields = ['tipo_cliente', 'empresa', 'servicio', 'producto', 'fecha_registra']
    can_delete = True
    fk_name = 'cliente'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo_identificacion',
        'numero_identificacion',
        'telefono',
        'correo',
        'estado',
        'fecha_registro',
    ]
    list_filter = ['estado']
    search_fields = ['nombre', 'numero_identificacion', 'correo', 'telefono']
    readonly_fields = ['fecha_registro', 'fecha_elimina', 'usuario_registra', 'usuario_elimina']
    inlines = [FormularioClienteInline, HistorialEstadoVentaInline, ClienteEmpresaInline]
    ordering = ['-fecha_registro']


@admin.register(FormularioCliente)
class FormularioClienteAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'nombre_campo', 'respuesta_campo', 'estado', 'fecha_registra']
    list_filter = ['estado', 'cliente']
    search_fields = ['nombre_campo', 'respuesta_campo', 'cliente__nombre']
    readonly_fields = ['fecha_registra', 'fecha_elimina', 'usuario_registra', 'usuario_elimina']


@admin.register(HistorialEstadoVenta)
class HistorialEstadoVentaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'estado', 'estado_registro', 'activo', 'fecha_registra']
    list_filter = ['activo', 'estado', 'estado_registro']
    search_fields = ['cliente__nombre', 'estado']


@admin.register(ClienteEmpresa)
class ClienteEmpresaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_cliente', 'empresa', 'servicio', 'producto', 'estado', 'fecha_registra']
    list_filter = ['estado', 'empresa', 'servicio']
    search_fields = ['cliente__nombre', 'tipo_cliente', 'producto']
    readonly_fields = ['fecha_registra']
    autocomplete_fields = ['cliente', 'empresa', 'servicio']
