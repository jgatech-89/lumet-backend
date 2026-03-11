from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Empresa
from .serializers import EmpresaSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Empresas'],
        summary='Listar empresas',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre', required=False, type=str),
            OpenApiParameter(name='estado', description='Filtrar por estado: 1=Activa, 0=Inactiva. Omitir = todos', required=False, type=str, enum=['1', '0']),
        ],
    ),
    create=extend_schema(tags=['Empresas'], summary='Crear empresa'),
    retrieve=extend_schema(tags=['Empresas'], summary='Obtener empresa'),
    update=extend_schema(tags=['Empresas'], summary='Actualizar empresa (PUT)'),
    partial_update=extend_schema(tags=['Empresas'], summary='Actualizar empresa (PATCH)'),
    destroy=extend_schema(tags=['Empresas'], summary='Eliminar empresa (borrado lógico)'),
)
class EmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        qs = Empresa.objects.filter(estado='1').select_related(
            'usuario_registra', 'usuario_edita', 'usuario_elimina'
        )
        estado = self.request.query_params.get('estado')
        if estado in ('1', '0'):
            qs = qs.filter(estado_empresa=estado)
        return qs.order_by('nombre')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'mensaje': 'Empresa creada exitosamente.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)

    
    # actualizar empresa
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'mensaje': 'Empresa actualizada exitosamente.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(usuario_edita=self.request.user)
        

    # eliminar empresa (borrado lógico)
    def destroy(self, request, *args, **kwargs):
        """Borrado lógico con mensaje personalizado"""
        instance = self.get_object()
        instance.estado = '0' 
        instance.usuario_elimina = request.user
        instance.fecha_elimina = timezone.now()
        instance.save()
        
        return Response(
            {'mensaje': 'Empresa eliminada correctamente.'},
            status=status.HTTP_200_OK
        )