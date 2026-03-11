from django.db import models
from apps.persona.models import Persona
from apps.persona.choices import ESTADO
from apps.empresa.models import Empresa


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    estado_servicio = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='1',
        help_text='Independiente de estado. 1=activo para uso, 0=inactivo (ej. oculto o deshabilitado). El frontend lo gestiona en edición.',
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='servicios',
    )
    usuario_registra = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='servicios_registrados',
        null=True,
        blank=True,
    )
    usuario_edita = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='servicios_editados',
        null=True,
        blank=True,
    )
    usuario_elimina = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name='servicios_eliminados',
        null=True,
        blank=True,
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_edita = models.DateTimeField(auto_now=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
