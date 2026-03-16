import django_filters
from .models import Campo, CampoOpcion


class CampoFilter(django_filters.FilterSet):
    """Filtros para el listado de Campos."""
    servicio = django_filters.NumberFilter(field_name='servicio_id')
    contratista = django_filters.NumberFilter(field_name='contratista_id')
    activo = django_filters.BooleanFilter(field_name='activo')
    producto = django_filters.CharFilter(field_name='producto', lookup_expr='iexact')
    seccion = django_filters.CharFilter(field_name='seccion', lookup_expr='iexact')

    class Meta:
        model = Campo
        fields = ['servicio', 'contratista', 'activo', 'producto', 'seccion']


class CampoOpcionFilter(django_filters.FilterSet):
    """Filtros para el listado de opciones de campo."""
    campo = django_filters.NumberFilter(field_name='campo_id')
    activo = django_filters.BooleanFilter(field_name='activo')

    class Meta:
        model = CampoOpcion
        fields = ['campo', 'activo']
