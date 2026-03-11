from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .choices import ESTADO, ESTADO_VENDEDOR, PERFIL, TIPO_IDENTIFICACION


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
    verificado = models.BooleanField(default=False)
    codigo_verificado = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='personas_creadas', verbose_name='Creado por')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='personas_actualizadas', verbose_name='Actualizado por')
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='personas_eliminadas', verbose_name='Eliminado por')

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


class Vendedor(models.Model):
    nombre_completo = models.CharField(max_length=255)
    tipo_identificacion = models.CharField(max_length=10, choices=TIPO_IDENTIFICACION, blank=True)
    numero_identificacion = models.CharField(max_length=50, db_index=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    estado_vendedor = models.CharField(max_length=20, choices=ESTADO_VENDEDOR, default='1', verbose_name='Estado vendedor')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='vendedores_creados', verbose_name='Creado por',)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='vendedores_actualizados', verbose_name='Actualizado por',)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='vendedores_eliminados', verbose_name='Eliminado por',)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        constraints = [
            models.UniqueConstraint(
                fields=['tipo_identificacion', 'numero_identificacion'],
                condition=models.Q(deleted_at__isnull=True),
                name='vendedor_tipo_num_id_uniq_activo',
            ),
        ]

    def delete(self, using=None, keep_parents=False):
        """Eliminación lógica: marca deleted_at (deleted_by se asigna desde la vista)."""
        self.deleted_at = timezone.now()
        update_fields = ['deleted_at', 'updated_at']
        if self.deleted_by_id is not None:
            update_fields.append('deleted_by_id')
        self.save(update_fields=update_fields)

    def __str__(self):
        return self.nombre_completo
