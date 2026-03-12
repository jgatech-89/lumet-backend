import django_filters
from .models import Campo, CampoOpcion


class CampoFilter(django_filters.FilterSet):
    """Filtros para el listado de Campos."""
    empresa = django_filters.NumberFilter(field_name='empresa_id')
    servicio = django_filters.NumberFilter(field_name='servicio_id')
    activo = django_filters.BooleanFilter(field_name='activo')

    class Meta:
        model = Campo
        fields = ['empresa', 'servicio', 'activo']


class CampoOpcionFilter(django_filters.FilterSet):
    """Filtros para el listado de opciones de campo."""
    campo = django_filters.NumberFilter(field_name='campo_id')
    activo = django_filters.BooleanFilter(field_name='activo')

    class Meta:
        model = CampoOpcion
        fields = ['campo', 'activo']
