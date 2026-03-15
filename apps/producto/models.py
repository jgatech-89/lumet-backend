from django.db import models
from django.utils import timezone
from apps.core.choices import ESTADO, ESTADO_PRODUCTO


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO, default='1')
    estado_producto = models.CharField(max_length=20,  choices=ESTADO_PRODUCTO, default='1', verbose_name='Estado producto', help_text='Independiente de estado. 1=activo para uso, 0=inactivo (ej. deshabilitado). El frontend lo gestiona en edición.',)
    fecha_registra = models.DateTimeField(auto_now_add=True)
    usuario_registra = models.ForeignKey(
        'persona.Persona',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_registrados',
        verbose_name='Usuario registra',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'persona.Persona',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_actualizados',
        verbose_name='Actualizado por',
    )
    fecha_elimina = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_elimina = models.ForeignKey(
        'persona.Persona',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_eliminados',
        verbose_name='Usuario elimina',
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def delete(self, using=None, keep_parents=False):
        """Eliminación lógica: marca fecha_elimina y estado=0 (usuario_elimina se asigna desde la vista)."""
        self.fecha_elimina = timezone.now()
        self.estado = '0'
        update_fields = ['fecha_elimina', 'estado', 'updated_at']
        if self.usuario_elimina_id is not None:
            update_fields.append('usuario_elimina_id')
        self.save(update_fields=update_fields)

    def __str__(self):
        return self.nombre
