from django.db import models
from apps.persona.models import Persona
from apps.persona.choices import ESTADO, ESTADO_VENDEDOR

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')  # 1=no eliminada, 0=eliminada
    estado_empresa = models.CharField(
        max_length=20, choices=ESTADO_VENDEDOR, default='1',
        verbose_name='Estado empresa'
    )  # 1=Activa, 0=Inactiva (editable)
    usuario_registra = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='empresas_registradas',null=True, blank=True)
    usuario_edita = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='empresas_editadas', null=True, blank=True)
    usuario_elimina = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='empresas_eliminadas', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_edita = models.DateTimeField(auto_now=True)
    fecha_elimina = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre