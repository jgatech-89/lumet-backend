from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Contratista
from .serializers import ContratistaSerializer
from .filters import ContratistaFilter


@extend_schema_view(
    list=extend_schema(
        tags=['Contratistas'],
        summary='Listar contratistas',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre de contratista', required=False, type=str),
            OpenApiParameter(name='estado', description='Filtrar por estado: 1=Activa, 0=Inactiva. Omitir = todos', required=False, type=str, enum=['1', '0']),
        ],
    ),
    create=extend_schema(tags=['Contratistas'], summary='Crear contratista'),
    retrieve=extend_schema(tags=['Contratistas'], summary='Obtener contratista'),
    update=extend_schema(tags=['Contratistas'], summary='Actualizar contratista (PUT)'),
    partial_update=extend_schema(tags=['Contratistas'], summary='Actualizar contratista (PATCH)'),
    destroy=extend_schema(tags=['Contratistas'], summary='Eliminar contratista (borrado lógico)'),
)
class ContratistaViewSet(viewsets.ModelViewSet):
    serializer_class = ContratistaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ContratistaFilter
    search_fields = ['nombre']

    def get_queryset(self):
        qs = Contratista.objects.filter(estado='1').select_related(
            'usuario_registra',
            'usuario_edita',
            'usuario_elimina',
        )
        estado = self.request.query_params.get('estado')
        if estado in ('1', '0'):
            qs = qs.filter(estado_contratista=estado)
        return qs.order_by('nombre')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Contratista creado exitosamente.',
            'data': serializer.data,
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
            'mensaje': 'Contratista actualizado exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(usuario_edita=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estado = '0'
        instance.estado_contratista = '0'
        instance.usuario_elimina = request.user
        instance.fecha_elimina = timezone.now()
        instance.save()
        return Response(
            {'mensaje': 'Contratista eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )
