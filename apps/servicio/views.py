from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Servicio
from .serializers import ServicioSerializer, ServicioMinimalSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Servicios'],
        summary='Listar servicios',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre', required=False, type=str),
            OpenApiParameter(name='estado', description='Filtrar por estado: 1=Activa, 0=Inactiva. Omitir = todos', required=False, type=str, enum=['1', '0']),
        ],
    ),
    create=extend_schema(tags=['Servicios'], summary='Crear servicio'),
    retrieve=extend_schema(tags=['Servicios'], summary='Obtener servicio'),
    update=extend_schema(tags=['Servicios'], summary='Actualizar servicio (PUT)'),
    partial_update=extend_schema(tags=['Servicios'], summary='Actualizar servicio (PATCH)'),
    destroy=extend_schema(tags=['Servicios'], summary='Eliminar servicio (borrado lógico)'),
)
class ServicioViewSet(viewsets.ModelViewSet):
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        qs = Servicio.objects.filter(estado='1').select_related(
            'usuario_registra', 'usuario_edita', 'usuario_elimina'
        )
        estado = self.request.query_params.get('estado')
        if estado in ('1', '0'):
            qs = qs.filter(estado_servicio=estado)
        return qs.order_by('nombre')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Servicio creado exitosamente.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'mensaje': 'Servicio actualizado exitosamente.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(usuario_edita=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Borrado lógico con mensaje personalizado"""
        instance = self.get_object()
        instance.estado = '0'
        instance.usuario_elimina = request.user
        instance.fecha_elimina = timezone.now()
        instance.save()
        return Response(
            {'mensaje': 'Servicio eliminado correctamente.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=['Servicios'],
        summary='Listado de servicios activos para selectores',
        description='Devuelve solo id y nombre de servicios activos (estado_servicio=1). Uso: dropdowns en formularios.',
    )
    @action(detail=False, url_path='activas', methods=['get'])
    def activas(self, request):
        """Listado mínimo (id, nombre) de servicios activos para uso en selectores."""
        qs = Servicio.objects.filter(estado='1', estado_servicio='1').order_by('nombre')
        serializer = ServicioMinimalSerializer(qs, many=True)
        return Response(serializer.data)