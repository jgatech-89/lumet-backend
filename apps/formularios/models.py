from django.db import models
from django.utils import timezone

from apps.empresa.models import Empresa
from apps.servicio.models import Servicio
from apps.persona.models import Persona
from apps.core.choices import ESTADO, TIPO_CAMPO


class Campo(models.Model):
    """Campo dinámico configurable para formularios por empresa y servicio."""
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CAMPO)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='campos_formulario')
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='campos_formulario')
    placeholder = models.CharField(max_length=255, blank=True, default='')
    orden = models.PositiveIntegerField(default=0)
    help_text = models.CharField(max_length=500, blank=True, default='')
    default_value = models.CharField(max_length=500, blank=True, default='')
    visible_si = models.CharField(max_length=500, blank=True, default='', help_text='Condición opcional para mostrar el campo según el valor de otro (uso futuro).')
    requerido = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_creados', verbose_name='Creado por')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_actualizados', verbose_name='Actualizado por')
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, related_name='campos_formulario_eliminados', verbose_name='Eliminado por')

    class Meta:
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'
        ordering = ['orden', 'id']

    def delete(self, using=None, keep_parents=False):
        """Eliminación lógica: marca deleted_at."""
        self.deleted_at = timezone.now()
        update_fields = ['deleted_at', 'updated_at']
        if self.deleted_by_id is not None:
            update_fields.append('deleted_by_id')
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

    class Meta:
        verbose_name = 'Opción de campo'
        verbose_name_plural = 'Opciones de campo'
        ordering = ['orden', 'id']

    def __str__(self):
        return f'{self.campo.nombre}: {self.label}'
