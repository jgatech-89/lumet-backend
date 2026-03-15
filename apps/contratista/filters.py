import django_filters
from .models import Contratista


class ContratistaFilter(django_filters.FilterSet):
    """Filtros para el listado de Contratistas."""
    servicio = django_filters.NumberFilter(field_name='servicio_id')

    class Meta:
        model = Contratista
        fields = ['servicio']
