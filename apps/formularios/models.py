from django.db import models
from django.utils import timezone

from apps.servicio.models import Servicio
from apps.contratista.models import Contratista
from apps.persona.models import Persona
from apps.core.choices import ESTADO, TIPO_CAMPO, SECCIONES_FORMULARIO


class Campo(models.Model):
    """Campo dinámico configurable para formularios por servicio y contratista."""
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CAMPO)
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='campos_formulario',
        null=True,
        blank=True,
        help_text='Si es null, aplica a todos los servicios.'
    )
    contratista = models.ForeignKey(
        Contratista,
        on_delete=models.PROTECT,
        related_name='campos_formulario',
        null=True,
        blank=True,
        help_text='Si es null, aplica a todos los contratistas del servicio.'
    )
    producto = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Valor de la opción del campo Producto al que pertenece este campo (opciones de otro campo).'
    )
    placeholder = models.CharField(max_length=255, blank=True, default='')
    seccion = models.CharField(
        max_length=30,
        choices=SECCIONES_FORMULARIO,
        default='campos_formulario',
        help_text='Sección del formulario a la que pertenece el campo.',
    )
    orden = models.PositiveIntegerField(default=0)
    visible_si = models.CharField(max_length=500, blank=True, default='', help_text='Condición opcional para mostrar el campo según el valor de otro (uso futuro).')
    requerido = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    fecha_registra = models.DateTimeField(auto_now_add=True)
    usuario_registra = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_registrados', verbose_name='Usuario registra')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_actualizados', verbose_name='Actualizado por')
    fecha_elimina = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_elimina = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_eliminados', verbose_name='Usuario elimina')

    class Meta:
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'
        ordering = ['seccion', 'orden', 'id']

    def delete(self, using=None, keep_parents=False):
        """Eliminación lógica: marca fecha_elimina y estado=0."""
        self.fecha_elimina = timezone.now()
        self.estado = '0'
        update_fields = ['fecha_elimina', 'estado', 'updated_at']
        if self.usuario_elimina_id is not None:
            update_fields.append('usuario_elimina_id')
        self.save(update_fields=update_fields)

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'


class CampoOpcion(models.Model):
    """Opción para campos tipo select."""
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='opciones')
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    fecha_registra = models.DateTimeField(auto_now_add=True)
    usuario_registra = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campo_opciones_registradas', verbose_name='Usuario registra')
    fecha_elimina = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_elimina = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campo_opciones_eliminadas', verbose_name='Usuario elimina')

    class Meta:
        verbose_name = 'Opción de campo'
        verbose_name_plural = 'Opciones de campo'
        ordering = ['orden', 'id']

    def __str__(self):
        return f'{self.campo.nombre}: {self.label}'
