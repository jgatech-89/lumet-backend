from django.db import models
from apps.persona.models import Persona
from apps.core.choices import ESTADO, ESTADO_CONTRATISTA


class Contratista(models.Model):
    """
    Contratista. La relación con Servicio (y otras entidades) se gestiona
    mediante la app relaciones (relaciones dinámicas).
    """
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    estado_contratista = models.CharField(max_length=20, choices=ESTADO_CONTRATISTA, default='1', verbose_name='Estado del contratista', help_text='Independiente de estado. 1=activo para uso, 0=inactivo (ej. oculto o deshabilitado). El frontend lo gestiona en edición.')
    usuario_registra = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='contratistas_registrados', null=True, blank=True)
    usuario_edita = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='contratistas_editados', null=True, blank=True)
    usuario_elimina = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='contratistas_eliminados', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_edita = models.DateTimeField(auto_now=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Contratista'
        verbose_name_plural = 'Contratistas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
