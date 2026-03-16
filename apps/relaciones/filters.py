"""
Filtros para el listado de Relaciones.
"""
import django_filters
from apps.core.choices import ESTADO, TIPO_RELACION
from .models import Relacion


class RelacionFilter(django_filters.FilterSet):
    """Filtros por origen, destino, tipo de relación y estado."""

    origen_tipo = django_filters.CharFilter(field_name='origen_tipo', lookup_expr='iexact')
    origen_id = django_filters.NumberFilter(field_name='origen_id')
    destino_tipo = django_filters.CharFilter(field_name='destino_tipo', lookup_expr='iexact')
    destino_id = django_filters.NumberFilter(field_name='destino_id')
    tipo_relacion = django_filters.ChoiceFilter(field_name='tipo_relacion', choices=TIPO_RELACION)
    estado = django_filters.ChoiceFilter(field_name='estado', choices=ESTADO)

    class Meta:
        model = Relacion
        fields = ['origen_tipo', 'origen_id', 'destino_tipo', 'destino_id', 'tipo_relacion', 'estado']
