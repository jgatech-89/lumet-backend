"""
Modelos de la app relaciones.

Permite definir relaciones dinámicas entre entidades del sistema
(Servicio, Contratista, Producto, Campo, Vendedor) sin ForeignKeys directos.
"""
from django.db import models
from apps.core.choices import TIPO_ENTIDAD_RELACION, TIPO_RELACION, ESTADO


class Relacion(models.Model):
    """
    Relación genérica entre dos entidades del sistema.

    Ejemplo: origen_tipo=servicio, origen_id=1, destino_tipo=contratista, destino_id=2
    significa "Servicio 1 → Contratista 2". Se usa para formularios dinámicos
    y selects dependientes en el frontend.
    """
    origen_tipo = models.CharField(
        max_length=20,
        choices=TIPO_ENTIDAD_RELACION,
        verbose_name='Tipo de entidad origen',
    )
    origen_id = models.PositiveIntegerField(verbose_name='ID entidad origen')
    destino_tipo = models.CharField(
        max_length=20,
        choices=TIPO_ENTIDAD_RELACION,
        verbose_name='Tipo de entidad destino',
    )
    destino_id = models.PositiveIntegerField(verbose_name='ID entidad destino')
    tipo_relacion = models.CharField(
        max_length=30,
        choices=TIPO_RELACION,
        default='estructura',
        verbose_name='Tipo de relación',
        help_text='estructura: dependencias entre entidades; contexto_campo: cuándo un campo aplica en el formulario.',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='1',
        verbose_name='Estado',
        help_text='1 = activa, 0 = inactiva (no se elimina físicamente)',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Relación'
        verbose_name_plural = 'Relaciones'
        ordering = ['origen_tipo', 'origen_id', 'destino_tipo', 'destino_id']
        indexes = [
            models.Index(fields=['origen_tipo', 'origen_id'], name='rel_origen_idx'),
            models.Index(fields=['destino_tipo', 'destino_id'], name='rel_destino_idx'),
        ]

    def __str__(self):
        return f'{self.origen_tipo}({self.origen_id}) → {self.destino_tipo}({self.destino_id})'
