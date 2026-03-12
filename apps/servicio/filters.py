import django_filters
from .models import Servicio


class ServicioFilter(django_filters.FilterSet):
    """Filtros para el listado de Servicios."""
    empresa = django_filters.NumberFilter(field_name='empresa_id')

    class Meta:
        model = Servicio
        fields = ['empresa']
