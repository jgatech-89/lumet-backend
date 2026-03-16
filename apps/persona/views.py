from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Persona, Vendedor
from .serializers import PersonaSerializer, VendedorSerializer, VendedorListSerializer


@extend_schema_view(
    list=extend_schema(tags=['Personas'], summary='Listar personas'),
    create=extend_schema(tags=['Personas'], summary='Crear persona'),
    retrieve=extend_schema(tags=['Personas'], summary='Obtener persona'),
    update=extend_schema(tags=['Personas'], summary='Actualizar persona (PUT)'),
    partial_update=extend_schema(tags=['Personas'], summary='Actualizar persona (PATCH)'),
    destroy=extend_schema(tags=['Personas'], summary='Eliminar persona'),
)
class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.filter(estado='1')
    serializer_class = PersonaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema_view(
    list=extend_schema(
        tags=['Vendedores'],
        summary='Listar vendedores',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre o número de identificación', required=False, type=str),
            OpenApiParameter(name='estado', description='Filtrar por estado: 1=Activo, 0=Inactivo. Omitir = todos', required=False, type=str, enum=['1', '0']),
        ],
    ),
    create=extend_schema(tags=['Vendedores'], summary='Crear vendedor'),
    retrieve=extend_schema(tags=['Vendedores'], summary='Obtener vendedor'),
    update=extend_schema(tags=['Vendedores'], summary='Actualizar vendedor (PUT)'),
    partial_update=extend_schema(tags=['Vendedores'], summary='Actualizar vendedor (PATCH)'),
    destroy=extend_schema(tags=['Vendedores'], summary='Eliminar vendedor (soft delete)'),
)
class VendedorViewSet(viewsets.ModelViewSet):
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['nombre_completo', 'numero_identificacion']

    def get_queryset(self):
        qs = Vendedor.objects.filter(fecha_elimina__isnull=True).select_related(
            'usuario_registra', 'updated_by', 'usuario_elimina'
        )
        estado = self.request.query_params.get('estado')
        if estado in ('1', '0'):
            qs = qs.filter(estado_vendedor=estado)
        return qs.order_by('-fecha_registra')

    def get_serializer_class(self):
        if self.action == 'list':
            return VendedorListSerializer
        return VendedorSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.usuario_elimina = self.request.user
        instance.delete()
