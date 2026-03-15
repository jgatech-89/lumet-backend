from django.db import models
from apps.persona.models import Persona
from apps.core.choices import ESTADO, ESTADO_SERVICIO


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    estado_servicio = models.CharField(max_length=20, choices=ESTADO_SERVICIO, default='1', verbose_name='Estado del servicio')
    usuario_registra = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='servicios_principal_registrados', null=True, blank=True)
    usuario_edita = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='servicios_principal_editados', null=True, blank=True)
    usuario_elimina = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='servicios_principal_eliminados', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_edita = models.DateTimeField(auto_now=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre