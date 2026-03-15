from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Producto
from .serializers import ProductoSerializer, ProductoListSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Productos'],
        summary='Listar productos',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre', required=False, type=str),
            OpenApiParameter(
                name='estado',
                description='Filtrar por estado producto: 1=Activo, 0=Inactivo. Omitir = todos',
                required=False,
                type=str,
                enum=['1', '0'],
            ),
        ],
    ),
    create=extend_schema(tags=['Productos'], summary='Crear producto'),
    retrieve=extend_schema(tags=['Productos'], summary='Obtener producto'),
    update=extend_schema(tags=['Productos'], summary='Actualizar producto (PUT)'),
    partial_update=extend_schema(tags=['Productos'], summary='Actualizar producto (PATCH)'),
    destroy=extend_schema(tags=['Productos'], summary='Eliminar producto (borrado lógico)'),
)
class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        qs = Producto.objects.filter(fecha_elimina__isnull=True).select_related(
            'usuario_registra',
            'updated_by',
            'usuario_elimina',
        )
        estado = self.request.query_params.get('estado')
        if estado in ('1', '0'):
            qs = qs.filter(estado_producto=estado)
        return qs.order_by('nombre')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Producto creado exitosamente.',
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
            'mensaje': 'Producto actualizado exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.usuario_elimina = self.request.user
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'mensaje': 'Producto eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )
