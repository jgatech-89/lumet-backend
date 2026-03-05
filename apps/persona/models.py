from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import ESTADO, PERFIL, TIPO_IDENTIFICACION


class Persona(AbstractUser):
    tipo_identificacion = models.CharField(max_length=10, choices=TIPO_IDENTIFICACION,)
    identificacion = models.CharField(max_length=50, db_index=True)
    primer_nombre = models.CharField(max_length=150, blank=True)
    segundo_nombre = models.CharField(max_length=100, blank=True)
    primer_apellido = models.CharField(max_length=150, blank=True)
    segundo_apellido = models.CharField(max_length=100, blank=True)
    correo = models.EmailField(max_length=254, blank=True)
    correo_auth = models.EmailField(max_length=254, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    perfil = models.CharField(max_length=20, choices=PERFIL, default='usuario')
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    verificado = models.BooleanField(default=False)
    codigo_verificado = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        constraints = [models.UniqueConstraint(fields=['tipo_identificacion', 'identificacion'], name='persona_tipo_id_identificacion_uniq')]

    def save(self, *args, **kwargs):
        self.first_name = self.primer_nombre or self.first_name
        self.last_name = self.primer_apellido or self.last_name
        self.email = self.correo or self.email
        self.primer_nombre = self.first_name or self.primer_nombre
        self.primer_apellido = self.last_name or self.primer_apellido
        self.correo = self.email or self.correo
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        partes = [self.primer_nombre, self.segundo_nombre, self.primer_apellido, self.segundo_apellido]
        return ' '.join(p for p in partes if p).strip() or '—'

    def __str__(self):
        return self.nombre_completo
