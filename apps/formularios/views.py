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
from .services import get_campos_formulario, reordenar_campos_para_insertar
from apps.core.choices import ESTADO_VENTA


@extend_schema_view(
    list=extend_schema(
        tags=['Formularios - Campos'],
        summary='Listar campos',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre de campo', required=False, type=str),
            OpenApiParameter(name='empresa', description='Filtrar por ID de empresa', required=False, type=int),
            OpenApiParameter(name='servicio', description='Filtrar por ID de servicio', required=False, type=int),
            OpenApiParameter(name='activo', description='Filtrar por activo (true/false)', required=False, type=bool),
            OpenApiParameter(name='producto', description='Filtrar por producto (valor del campo)', required=False, type=str),
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
            .filter(fecha_elimina__isnull=True)
            .select_related('empresa', 'servicio', 'usuario_registra', 'updated_by', 'usuario_elimina')
            .prefetch_related('opciones')
            .order_by('seccion', 'orden', 'id')
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
        data = serializer.validated_data
        empresa_id = data.get('empresa')
        empresa_id = empresa_id.pk if hasattr(empresa_id, 'pk') else empresa_id
        servicio_id = data.get('servicio')
        servicio_id = servicio_id.pk if hasattr(servicio_id, 'pk') else servicio_id
        producto = (data.get('producto') or '').strip()
        seccion = data.get('seccion', 'campos_formulario')
        orden = data.get('orden', 0)
        reordenar_campos_para_insertar(empresa_id, servicio_id, producto, seccion, orden, excluir_campo_id=None)
        serializer.save(usuario_registra=self.request.user)

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
        instance = serializer.instance
        data = serializer.validated_data
        empresa_id = instance.empresa_id
        servicio_id = instance.servicio_id
        producto = (instance.producto or '').strip()
        seccion = data.get('seccion', instance.seccion)
        orden = data.get('orden', instance.orden)
        reordenar_campos_para_insertar(empresa_id, servicio_id, producto, seccion, orden, excluir_campo_id=instance.pk)
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fecha_elimina = timezone.now()
        instance.usuario_elimina = request.user
        instance.estado = '0'
        instance.save(update_fields=['fecha_elimina', 'usuario_elimina', 'estado', 'updated_at'])
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
        return (
            CampoOpcion.objects
            .filter(estado='1')
            .select_related('campo')
            .order_by('campo', 'orden', 'id')
        )

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)

    def perform_destroy(self, instance):
        instance.fecha_elimina = timezone.now()
        instance.usuario_elimina = self.request.user
        instance.estado = '0'
        instance.save(update_fields=['fecha_elimina', 'usuario_elimina', 'estado'])

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
            campo = Campo.objects.get(pk=campo_id, fecha_elimina__isnull=True)
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
                usuario_registra=self.request.user,
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
    summary='Opciones de un campo por nombre (ej. Producto)',
    parameters=[
        OpenApiParameter(name='nombre', description='Nombre del campo (ej. producto, Producto)', required=True, type=str),
        OpenApiParameter(name='empresa_id', description='ID de empresa para filtrar opciones por servicio (opcional)', required=False, type=int),
        OpenApiParameter(name='servicio_id', description='ID de servicio para filtrar opciones (opcional)', required=False, type=int),
    ],
    responses={200: {'type': 'array', 'items': {'type': 'object', 'properties': {'value': {'type': 'string'}, 'label': {'type': 'string'}}}}},
)
class OpcionesCampoPorNombreAPIView(APIView):
    """
    GET /api/campos/opciones-por-nombre/?nombre=producto&empresa_id=1&servicio_id=2
    Devuelve las opciones (CampoOpcion) de un campo cuyo nombre coincida (case-insensitive).
    Si se pasan empresa_id y servicio_id, prioriza el campo más específico (empresa+servicio > empresa > global).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q

        nombre = (request.query_params.get('nombre') or '').strip()
        if not nombre:
            return Response(
                {'error': 'Se requiere el parámetro "nombre".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        empresa_id = request.query_params.get('empresa_id')
        servicio_id = request.query_params.get('servicio_id')
        try:
            empresa_id = int(empresa_id) if empresa_id is not None else None
            servicio_id = int(servicio_id) if servicio_id is not None else None
        except (TypeError, ValueError):
            empresa_id = servicio_id = None

        # Para "producto": buscar también Productos, Tipo producto, tipo de producto
        nombres_producto = ['producto', 'Productos', 'Tipo producto', 'tipo de producto']
        nombre_lower = nombre.lower().strip()
        if nombre_lower in ('producto', 'productos', 'tipo producto', 'tipo de producto'):
            q_nombres = Q()
            for n in nombres_producto:
                q_nombres |= Q(nombre__iexact=n)
            qs = Campo.objects.filter(
                fecha_elimina__isnull=True,
                tipo='select',
            ).filter(q_nombres).prefetch_related('opciones')
        else:
            qs = Campo.objects.filter(
                fecha_elimina__isnull=True,
                nombre__iexact=nombre,
                tipo='select',
            ).prefetch_related('opciones')

        if empresa_id is not None and servicio_id is not None:
            qs = qs.filter(
                Q(empresa_id=empresa_id, servicio_id=servicio_id)
                | Q(empresa_id=empresa_id, servicio_id__isnull=True)
                | Q(empresa_id__isnull=True, servicio_id__isnull=True)
            ).order_by('-empresa_id', '-servicio_id')
            campo = qs.first()
            if not campo:
                return Response([])
            opciones = list(
                campo.opciones.filter(activo=True).order_by('orden', 'id').values('value', 'label')
            )
            return Response([{'value': o['value'], 'label': o['label']} for o in opciones])
        elif empresa_id is not None:
            qs = qs.filter(
                Q(empresa_id=empresa_id) | Q(empresa_id__isnull=True)
            ).order_by('-empresa_id')
            campo = qs.first()
            if not campo:
                return Response([])
            opciones = list(
                campo.opciones.filter(activo=True).order_by('orden', 'id').values('value', 'label')
            )
            return Response([{'value': o['value'], 'label': o['label']} for o in opciones])
        else:
            # Sin empresa_id/servicio_id: devolver TODAS las opciones de producto de todos los campos
            # (para "aplicar a todos los servicios y contratistas" - listado según como se creó)
            from apps.formularios.models import CampoOpcion
            opciones_qs = CampoOpcion.objects.filter(
                campo__in=qs,
                activo=True,
                estado='1',
            ).order_by('orden', 'id').values('value', 'label')
            seen = {}
            for o in opciones_qs:
                v = (o.get('value') or '').strip()
                l = (o.get('label') or v or '').strip()
                if v and v not in seen:
                    seen[v] = {'value': v, 'label': l or v}
            result = list(seen.values())
            return Response(result)


@extend_schema(
    tags=['Formularios'],
    summary='Opciones del campo Estado de venta',
    responses={200: {'type': 'array', 'items': {'type': 'object', 'properties': {'value': {'type': 'string'}, 'label': {'type': 'string'}}}}},
)
class OpcionesEstadoVentaAPIView(APIView):
    """
    GET /api/campos/opciones-estado-venta/
    Devuelve las opciones del campo "estado_venta" o "Estado de venta" desde CampoOpcion.
    Si no existe ese campo, devuelve las opciones por defecto de ESTADO_VENTA (choices).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nombres_buscar = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        campo = (
            Campo.objects
            .filter(fecha_elimina__isnull=True, nombre__in=nombres_buscar)
            .prefetch_related('opciones')
            .first()
        )
        if campo:
            opciones = list(
                campo.opciones.filter(activo=True).order_by('orden', 'id').values('value', 'label')
            )
            if opciones:
                return Response([{'value': o['value'], 'label': o['label']} for o in opciones])
        # Fallback a choices
        return Response([{'value': v, 'label': l} for v, l in ESTADO_VENTA])


@extend_schema(
    tags=['Formularios'],
    summary='Campos del formulario por empresa, servicio y producto',
    parameters=[
        OpenApiParameter(name='empresa_id', description='ID de la empresa (opcional si se piden campos globales)', required=False, type=int),
        OpenApiParameter(name='servicio_id', description='ID del servicio (opcional si se piden campos globales)', required=False, type=int),
        OpenApiParameter(name='producto', description='Valor del producto para filtrar campos (opcional)', required=False, type=str),
        OpenApiParameter(name='solo_sin_producto', description='Si true, solo devuelve campos sin restricción por producto', required=False, type=bool),
    ],
    responses={200: FormularioCampoSerializer(many=True)},
)
class FormularioCamposAPIView(APIView):
    """
    GET /api/formulario/?empresa_id=1&servicio_id=2&producto=luz
    Devuelve los campos configurados para el formulario (activos, ordenados, con opciones para select).
    Si no se pasan empresa_id ni servicio_id, devuelve campos globales.
    Si se pasa producto, filtra campos que aplican a ese producto (o producto vacío = todos).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')
        servicio_id = request.query_params.get('servicio_id')
        producto = (request.query_params.get('producto') or '').strip() or None
        solo_sin_producto = request.query_params.get('solo_sin_producto', '').lower() in ('true', '1', 'yes')
        if not empresa_id and not servicio_id:
            campos = get_campos_formulario(None, None, producto, solo_sin_producto)
        else:
            if not empresa_id or not servicio_id:
                return Response(
                    {'error': 'Se requieren ambos parámetros empresa_id y servicio_id, o ninguno para campos globales.'},
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
            campos = get_campos_formulario(empresa_id, servicio_id, producto, solo_sin_producto)
        serializer = FormularioCampoSerializer(campos, many=True)
        return Response(serializer.data)
