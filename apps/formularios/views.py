from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from .models import Campo, CampoOpcion
from .serializers import CampoReadSerializer, CampoWriteSerializer, CampoOpcionSerializer, FormularioCampoSerializer
from .filters import CampoFilter, CampoOpcionFilter
from .services import get_campos_formulario


@extend_schema_view(
    list=extend_schema(
        tags=['Formularios - Campos'],
        summary='Listar campos',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre de campo', required=False, type=str),
            OpenApiParameter(name='empresa', description='Filtrar por ID de empresa', required=False, type=int),
            OpenApiParameter(name='servicio', description='Filtrar por ID de servicio', required=False, type=int),
            OpenApiParameter(name='activo', description='Filtrar por activo (true/false)', required=False, type=bool),
        ],
    ),
    create=extend_schema(tags=['Formularios - Campos'], summary='Crear campo'),
    retrieve=extend_schema(tags=['Formularios - Campos'], summary='Obtener campo'),
    update=extend_schema(tags=['Formularios - Campos'], summary='Actualizar campo (PUT)'),
    partial_update=extend_schema(tags=['Formularios - Campos'], summary='Actualizar campo (PATCH)'),
    destroy=extend_schema(tags=['Formularios - Campos'], summary='Eliminar campo (borrado lógico)'),
)
class CampoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CampoFilter
    search_fields = ['nombre']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CampoReadSerializer
        return CampoWriteSerializer

    def get_queryset(self):
        return (
            Campo.objects
            .filter(deleted_at__isnull=True)
            .select_related('empresa', 'servicio', 'created_by', 'updated_by', 'deleted_by')
            .prefetch_related('opciones')
            .order_by('orden', 'id')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Campo creado exitosamente.',
            'data': CampoReadSerializer(serializer.instance).data,
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'mensaje': 'Campo actualizado exitosamente.',
            'data': CampoReadSerializer(serializer.instance).data,
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.deleted_by = request.user
        instance.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])
        return Response(
            {'mensaje': 'Campo eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Formularios - Opciones'],
        summary='Listar opciones de campo',
        parameters=[
            OpenApiParameter(name='campo', description='Filtrar por ID de campo', required=False, type=int),
            OpenApiParameter(name='activo', description='Filtrar por activo', required=False, type=bool),
        ],
    ),
    create=extend_schema(tags=['Formularios - Opciones'], summary='Crear opción de campo'),
    retrieve=extend_schema(tags=['Formularios - Opciones'], summary='Obtener opción'),
    update=extend_schema(tags=['Formularios - Opciones'], summary='Actualizar opción (PUT)'),
    partial_update=extend_schema(tags=['Formularios - Opciones'], summary='Actualizar opción (PATCH)'),
    destroy=extend_schema(tags=['Formularios - Opciones'], summary='Eliminar opción'),
)
class CampoOpcionViewSet(viewsets.ModelViewSet):
    serializer_class = CampoOpcionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CampoOpcionFilter

    def get_queryset(self):
        return CampoOpcion.objects.select_related('campo').order_by('campo', 'orden', 'id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Opción de campo creada exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'mensaje': 'Opción de campo actualizada exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Formularios - Opciones'],
        summary='Crear varias opciones de un campo',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'campo': {'type': 'integer', 'description': 'ID del campo'},
                    'opciones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'label': {'type': 'string'},
                                'value': {'type': 'string'},
                                'orden': {'type': 'integer'},
                            },
                            'required': ['label', 'value'],
                        },
                    },
                },
                'required': ['campo', 'opciones'],
            },
        },
        responses={201: CampoOpcionSerializer(many=True)},
    )
    @action(detail=False, methods=['post'], url_path='crear-lote')
    def crear_lote(self, request):
        """Crea varias opciones para un campo en una sola petición."""
        campo_id = request.data.get('campo')
        opciones_data = request.data.get('opciones') or []
        if campo_id is None:
            return Response(
                {'error': 'Se requiere el campo "campo".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(opciones_data, list):
            return Response(
                {'error': '"opciones" debe ser una lista.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            campo = Campo.objects.get(pk=campo_id, deleted_at__isnull=True)
        except Campo.DoesNotExist:
            return Response(
                {'error': 'Campo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        created = []
        for i, item in enumerate(opciones_data):
            if not isinstance(item, dict):
                continue
            label = item.get('label') or ''
            value = item.get('value', label)
            orden = item.get('orden', i)
            opcion = CampoOpcion.objects.create(
                campo=campo,
                label=label,
                value=value,
                orden=orden,
                activo=True,
            )
            created.append(CampoOpcionSerializer(opcion).data)
        return Response(created, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Formularios - Opciones'],
        summary='Actualizar varias opciones de campo en lote',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'opciones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'label': {'type': 'string'},
                                'value': {'type': 'string'},
                                'orden': {'type': 'integer'},
                            },
                            'required': ['id'],
                        },
                    },
                },
                'required': ['opciones'],
            },
        },
        responses={200: CampoOpcionSerializer(many=True)},
    )
    @action(detail=False, methods=['post'], url_path='actualizar-lote')
    def actualizar_lote(self, request):
        """Actualiza varias opciones en una sola petición."""
        opciones_data = request.data.get('opciones') or []
        if not isinstance(opciones_data, list):
            return Response(
                {'error': '"opciones" debe ser una lista.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated = []
        for item in opciones_data:
            if not isinstance(item, dict):
                continue
            pk = item.get('id')
            if pk is None:
                continue
            try:
                opcion = CampoOpcion.objects.get(pk=pk)
            except CampoOpcion.DoesNotExist:
                continue
            if 'label' in item:
                opcion.label = item['label']
            if 'value' in item:
                opcion.value = item['value']
            if 'orden' in item:
                opcion.orden = item['orden']
            opcion.activo = True
            opcion.save()
            updated.append(CampoOpcionSerializer(opcion).data)
        return Response(updated, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Formularios'],
    summary='Campos del formulario por empresa y servicio',
    parameters=[
        OpenApiParameter(name='empresa_id', description='ID de la empresa', required=True, type=int),
        OpenApiParameter(name='servicio_id', description='ID del servicio', required=True, type=int),
    ],
    responses={200: FormularioCampoSerializer(many=True)},
)
class FormularioCamposAPIView(APIView):
    """
    GET /api/formulario/?empresa_id=1&servicio_id=2
    Devuelve los campos configurados para el formulario (activos, ordenados, con opciones para select).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')
        servicio_id = request.query_params.get('servicio_id')
        if not empresa_id or not servicio_id:
            return Response(
                {'error': 'Se requieren los parámetros empresa_id y servicio_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            empresa_id = int(empresa_id)
            servicio_id = int(servicio_id)
        except (TypeError, ValueError):
            return Response(
                {'error': 'empresa_id y servicio_id deben ser números.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campos = get_campos_formulario(empresa_id, servicio_id)
        serializer = FormularioCampoSerializer(campos, many=True)
        return Response(serializer.data)
