import django_filters
from .models import Contratista


class ContratistaFilter(django_filters.FilterSet):
    """Filtros para el listado de Contratistas (sin servicio; relaciones vía app relaciones)."""

    class Meta:
        model = Contratista
        fields = []
