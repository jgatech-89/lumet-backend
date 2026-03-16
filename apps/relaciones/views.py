"""
ViewSets para la API de relaciones dinámicas.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from .models import Relacion
from .serializers import RelacionSerializer, RelacionSimpleSerializer, OpcionDestinoSerializer
from .filters import RelacionFilter


def _nombres_por_tipo_e_id(destino_tipo, destino_ids):
    """Dado destino_tipo y lista de IDs, devuelve dict { id: nombre }."""
    if not destino_ids:
        return {}
    try:
        if destino_tipo == 'servicio':
            from apps.servicio.models import Servicio
            qs = Servicio.objects.filter(pk__in=destino_ids, estado='1').values_list('id', 'nombre')
        elif destino_tipo == 'contratista':
            from apps.contratista.models import Contratista
            qs = Contratista.objects.filter(pk__in=destino_ids, estado='1').values_list('id', 'nombre')
        elif destino_tipo == 'producto':
            from apps.producto.models import Producto
            qs = Producto.objects.filter(pk__in=destino_ids).values_list('id', 'nombre')
        elif destino_tipo == 'vendedor':
            from apps.persona.models import Persona
            qs = Persona.objects.filter(pk__in=destino_ids).values_list('id', 'nombre')
        elif destino_tipo == 'campo':
            from apps.formularios.models import Campo
            qs = Campo.objects.filter(pk__in=destino_ids, fecha_elimina__isnull=True).values_list('id', 'nombre')
        else:
            return {i: str(i) for i in destino_ids}
        return {r[0]: (r[1] or '') for r in qs}
    except Exception:
        return {i: str(i) for i in destino_ids}


@extend_schema_view(
    list=extend_schema(
        tags=['Relaciones'],
        summary='Listar relaciones',
        parameters=[
            OpenApiParameter('origen_tipo', str, description='Filtrar por tipo de entidad origen'),
            OpenApiParameter('origen_id', int, description='Filtrar por ID de entidad origen'),
            OpenApiParameter('destino_tipo', str, description='Filtrar por tipo de entidad destino'),
            OpenApiParameter('destino_id', int, description='Filtrar por ID de entidad destino'),
        ],
    ),
    create=extend_schema(tags=['Relaciones'], summary='Crear relación'),
    retrieve=extend_schema(tags=['Relaciones'], summary='Obtener relación'),
    update=extend_schema(tags=['Relaciones'], summary='Actualizar relación (PUT)'),
    partial_update=extend_schema(tags=['Relaciones'], summary='Actualizar relación (PATCH)'),
    destroy=extend_schema(tags=['Relaciones'], summary='Eliminar relación'),
)
class RelacionViewSet(viewsets.ModelViewSet):
    """
    CRUD de relaciones dinámicas entre entidades.
    Soporta filtros por origen_tipo, origen_id, destino_tipo, destino_id, estado.
    Por defecto solo se listan relaciones activas (estado='1').
    """
    queryset = Relacion.objects.filter(estado='1')
    serializer_class = RelacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RelacionFilter

    def get_queryset(self):
        return Relacion.objects.filter(estado='1').order_by(
            'origen_tipo', 'origen_id', 'destino_tipo', 'destino_id'
        )

    def create(self, request, *args, **kwargs):
        """Crea relación o reactiva una existente (estado='0' → '1') para evitar duplicados."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        existente = Relacion.objects.filter(
            origen_tipo=data['origen_tipo'],
            origen_id=data['origen_id'],
            destino_tipo=data['destino_tipo'],
            destino_id=data['destino_id'],
        ).first()
        if existente:
            existente.estado = '1'
            existente.save(update_fields=['estado'])
            out_serializer = RelacionSerializer(existente)
            return Response(out_serializer.data, status=200)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        """Desactiva la relación (estado='0') en lugar de borrarla físicamente."""
        instance = Relacion.objects.filter(pk=kwargs['pk']).first()
        if not instance:
            from rest_framework import status
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.estado = '0'
        instance.save(update_fields=['estado'])
        return Response(status=204)

    @extend_schema(
        tags=['Relaciones'],
        summary='Opciones para selects dependientes',
        description=(
            'Devuelve los destinos relacionados dado origen_tipo, origen_id y destino_tipo. '
            'Ej: origen_tipo=servicio, origen_id=1, destino_tipo=contratista → contratistas del servicio 1.'
        ),
        parameters=[
            OpenApiParameter('origen_tipo', str, required=True, description='Tipo de entidad origen'),
            OpenApiParameter('origen_id', int, required=True, description='ID de entidad origen'),
            OpenApiParameter('destino_tipo', str, required=True, description='Tipo de entidad destino'),
        ],
        responses={200: OpcionDestinoSerializer(many=True)},
    )
    @action(detail=False, url_path='opciones', methods=['get'])
    def opciones(self, request):
        """
        Endpoint optimizado para selects dependientes.
        Parámetros: origen_tipo, origen_id, destino_tipo.
        Devuelve lista de { id: destino_id, tipo: destino_tipo } sin duplicados.
        """
        origen_tipo = request.query_params.get('origen_tipo')
        origen_id = request.query_params.get('origen_id')
        destino_tipo = request.query_params.get('destino_tipo')

        if not all([origen_tipo, origen_id is not None, destino_tipo]):
            return Response(
                {'error': 'Se requieren origen_tipo, origen_id y destino_tipo'},
                status=400,
            )

        try:
            origen_id = int(origen_id)
        except (TypeError, ValueError):
            return Response({'error': 'origen_id debe ser un entero'}, status=400)

        qs = (
            Relacion.objects.filter(
                origen_tipo=origen_tipo,
                origen_id=origen_id,
                destino_tipo=destino_tipo,
                estado='1',
            )
            .values_list('destino_id', flat=True)
            .distinct()
            .order_by('destino_id')
        )
        destino_ids = list(qs)
        nombres = _nombres_por_tipo_e_id(destino_tipo, destino_ids)
        data = [
            {'id': i, 'tipo': destino_tipo, 'label': nombres.get(i, str(i))}
            for i in destino_ids
        ]
        serializer = OpcionDestinoSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
