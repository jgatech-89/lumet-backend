"""
Modelos de la app cliente: Cliente, FormularioCliente (respuestas dinámicas), HistorialEstadoVenta y ClienteEmpresa.
"""
from django.db import models
from django.utils import timezone

from apps.persona.models import Persona
from apps.empresa.models import Empresa
from apps.servicio.models import Servicio
from apps.core.choices import ESTADO, TIPO_IDENTIFICACION


class Cliente(models.Model):
    """Cliente registrado en el sistema. tipo_cliente, estado_venta y vendedor se manejan por campos dinámicos."""
    nombre = models.CharField(max_length=255)
    tipo_identificacion = models.CharField(max_length=10, choices=TIPO_IDENTIFICACION, blank=True)
    numero_identificacion = models.CharField(max_length=50, db_index=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=254, blank=True)
    direccion = models.CharField(max_length=500, blank=True, default='')
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    servicio_id = models.PositiveIntegerField(null=True, blank=True, help_text='ID del servicio seleccionado al crear el cliente')
    producto = models.CharField(max_length=255, blank=True, default='', help_text='Producto seleccionado al completar el cliente')
    usuario_registra = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='clientes_registrados',
        null=True,
        blank=True,
    )
    usuario_elimina = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='clientes_eliminados',
        null=True,
        blank=True,
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.nombre


class HistorialEstadoVenta(models.Model):
    """Historial de estados de venta por producto (cliente_empresa). Solo uno activo por cliente_empresa."""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='historial_estados_venta',
    )
    cliente_empresa = models.ForeignKey(
        'ClienteEmpresa',
        on_delete=models.CASCADE,
        related_name='historial_estados_venta',
        null=True,
        blank=True,
        help_text='Producto específico. Si es null, aplica al cliente (legacy).',
    )
    estado = models.CharField(max_length=50, help_text='Valor del estado de venta: pendiente, completada, etc.')
    estado_registro = models.CharField(max_length=20, choices=ESTADO, default='1', help_text='1=activo, 0=eliminado')
    activo = models.BooleanField(default=True)
    usuario_registra = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='historial_estado_venta_registrados',
        null=True,
        blank=True,
    )
    usuario_elimina = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='historial_estado_venta_eliminados',
        null=True,
        blank=True,
    )
    fecha_registra = models.DateTimeField(auto_now_add=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Historial estado de venta'
        verbose_name_plural = 'Historial estados de venta'
        ordering = ['-fecha_registra']

    def __str__(self):
        return f'{self.cliente_id} - {self.estado}'


class FormularioCliente(models.Model):
    """Respuesta dinámica de un campo del formulario, asociada a un cliente."""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='respuestas_formulario',
    )
    nombre_campo = models.CharField(max_length=255)
    respuesta_campo = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    usuario_registra = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='formulario_cliente_registrados',
        null=True,
        blank=True,
    )
    usuario_elimina = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='formulario_cliente_eliminados',
        null=True,
        blank=True,
    )
    fecha_registra = models.DateTimeField(auto_now_add=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Respuesta formulario cliente'
        verbose_name_plural = 'Respuestas formulario cliente'
        ordering = ['cliente', 'nombre_campo']
        unique_together = [['cliente', 'nombre_campo']]

    def __str__(self):
        return f'{self.cliente} - {self.nombre_campo}'


class ClienteEmpresa(models.Model):
    """
    Relación cliente + tipo_cliente + empresa + servicio + producto + vendedor.
    Centraliza la relación entre cliente, tipo, empresa, producto/servicio y formulario.
    El vendedor se asocia al producto vendido (ClienteEmpresa).
    Se crea al registrar un cliente nuevo y al agregar productos a clientes existentes.
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='cliente_empresas',
    )
    tipo_cliente = models.CharField(max_length=255, blank=True, default='')
    vendedor = models.ForeignKey(
        'persona.Vendedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cliente_empresas',
        verbose_name='Vendedor del producto',
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='cliente_empresas',
        null=True,
        blank=True,
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='cliente_empresas',
        null=True,
        blank=True,
    )
    producto = models.CharField(max_length=255, blank=True, default='')
    formulario_id = models.PositiveIntegerField(null=True, blank=True, help_text='Referencia a formulario/campo si aplica')
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    fecha_registra = models.DateTimeField(auto_now_add=True)
    usuario_registra = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cliente_empresas_registrados',
    )

    class Meta:
        verbose_name = 'Cliente empresa'
        verbose_name_plural = 'Cliente empresas'
        ordering = ['-fecha_registra']

    def __str__(self):
        emp = self.empresa.nombre if self.empresa_id else '-'
        return f'{self.cliente.nombre} - {emp} - {self.producto or "-"}'
