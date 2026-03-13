import django_filters
from django.db.models import Exists, OuterRef
from .models import Cliente, HistorialEstadoVenta


class ClienteFilter(django_filters.FilterSet):
    estado_venta = django_filters.CharFilter(method='filter_estado_venta')

    class Meta:
        model = Cliente
        fields = ['estado_venta']

    def filter_estado_venta(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            historial_estados_venta__activo=True,
            historial_estados_venta__estado__iexact=value
        )
