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
from .services import (
    get_campos_formulario,
    get_campos_formulario_por_producto_id,
    reordenar_campos_para_insertar,
)
from .services import _get_campos_base_campos_formulario, _filtrar_campos_por_contexto
from apps.core.choices import ESTADO_VENTA


@extend_schema_view(
    list=extend_schema(
        tags=['Formularios - Campos'],
        summary='Listar campos',
        parameters=[
            OpenApiParameter(name='search', description='Buscar por nombre de campo', required=False, type=str),
            OpenApiParameter(name='servicio', description='Filtrar por ID de servicio', required=False, type=int),
            OpenApiParameter(name='contratista', description='Filtrar por ID de contratista', required=False, type=int),
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
            .select_related('servicio', 'contratista', 'usuario_registra', 'updated_by', 'usuario_elimina')
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
        servicio_id = data.get('servicio')
        servicio_id = servicio_id.pk if hasattr(servicio_id, 'pk') else servicio_id
        contratista_id = data.get('contratista')
        contratista_id = contratista_id.pk if hasattr(contratista_id, 'pk') else contratista_id
        producto = (data.get('producto') or '').strip()
        seccion = data.get('seccion', 'campos_formulario')
        orden = data.get('orden', 0)
        reordenar_campos_para_insertar(servicio_id, contratista_id, producto, seccion, orden, excluir_campo_id=None)
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
        servicio_id = instance.servicio_id
        contratista_id = instance.contratista_id
        producto = (instance.producto or '').strip()
        seccion = data.get('seccion', instance.seccion)
        orden = data.get('orden', instance.orden)
        reordenar_campos_para_insertar(servicio_id, contratista_id, producto, seccion, orden, excluir_campo_id=instance.pk)
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
        OpenApiParameter(name='servicio_id', description='ID de servicio para filtrar opciones (opcional)', required=False, type=int),
        OpenApiParameter(name='contratista_id', description='ID de contratista para filtrar opciones (opcional)', required=False, type=int),
    ],
    responses={200: {'type': 'array', 'items': {'type': 'object', 'properties': {'value': {'type': 'string'}, 'label': {'type': 'string'}}}}},
)
class OpcionesCampoPorNombreAPIView(APIView):
    """
    GET /api/campos/opciones-por-nombre/?nombre=producto&servicio_id=1&contratista_id=2
    Devuelve las opciones (CampoOpcion) de un campo cuyo nombre coincida (case-insensitive).
    Si se pasan servicio_id y contratista_id, prioriza el campo más específico (servicio+contratista > servicio > global).
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
        servicio_id = request.query_params.get('servicio_id')
        contratista_id = request.query_params.get('contratista_id')
        try:
            servicio_id = int(servicio_id) if servicio_id is not None else None
            contratista_id = int(contratista_id) if contratista_id is not None else None
        except (TypeError, ValueError):
            servicio_id = contratista_id = None

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

        if servicio_id is not None and contratista_id is not None:
            qs = qs.filter(
                Q(servicio_id=servicio_id, contratista_id=contratista_id)
                | Q(servicio_id=servicio_id, contratista_id__isnull=True)
                | Q(servicio_id__isnull=True, contratista_id__isnull=True)
            ).order_by('-servicio_id', '-contratista_id')
            campo = qs.first()
            if not campo:
                return Response([])
            opciones = list(
                campo.opciones.filter(activo=True).order_by('orden', 'id').values('value', 'label')
            )
            return Response([{'value': o['value'], 'label': o['label']} for o in opciones])
        elif servicio_id is not None:
            qs = qs.filter(
                Q(servicio_id=servicio_id) | Q(servicio_id__isnull=True)
            ).order_by('-servicio_id')
            campo = qs.first()
            if not campo:
                return Response([])
            opciones = list(
                campo.opciones.filter(activo=True).order_by('orden', 'id').values('value', 'label')
            )
            return Response([{'value': o['value'], 'label': o['label']} for o in opciones])
        else:
            # Sin servicio_id/contratista_id: devolver TODAS las opciones de producto de todos los campos
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
    summary='Campos del formulario por servicio, contratista, producto y sección',
    parameters=[
        OpenApiParameter(name='servicio_id', description='ID del servicio (opcional si se piden campos globales)', required=False, type=int),
        OpenApiParameter(name='contratista_id', description='ID del contratista (opcional si se piden campos globales)', required=False, type=int),
        OpenApiParameter(name='producto', description='Valor del producto para filtrar campos (opcional)', required=False, type=str),
        OpenApiParameter(name='producto_id', description='ID del producto; en seccion=campos_formulario carga campos base + relacionados vía Relacion', required=False, type=int),
        OpenApiParameter(name='solo_sin_producto', description='Si true, solo devuelve campos sin restricción por producto', required=False, type=bool),
        OpenApiParameter(name='seccion', description='Filtrar por sección: cliente, datos_base, campos_formulario, vendedor', required=False, type=str),
    ],
    responses={200: FormularioCampoSerializer(many=True)},
)
class FormularioCamposAPIView(APIView):
    """
    GET /api/formulario/?servicio_id=1&contratista_id=2&seccion=campos_formulario
    Sin producto_id: solo campos base (selector de producto).
    GET /api/formulario/?servicio_id=1&contratista_id=2&producto_id=6&seccion=campos_formulario
    Con producto_id: campos base + campos relacionados al producto (tabla Relacion).
    Para otras secciones se mantiene el comportamiento por producto (valor).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        servicio_id = request.query_params.get('servicio_id')
        contratista_id = request.query_params.get('contratista_id')
        producto = (request.query_params.get('producto') or '').strip() or None
        producto_id_raw = request.query_params.get('producto_id')
        producto_id = None
        if producto_id_raw not in (None, ''):
            try:
                producto_id = int(producto_id_raw)
            except (TypeError, ValueError):
                pass
        solo_sin_producto = request.query_params.get('solo_sin_producto', '').lower() in ('true', '1', 'yes')
        seccion = (request.query_params.get('seccion') or '').strip() or None

        sid, cid = None, None
        if servicio_id and contratista_id:
            try:
                sid = int(servicio_id)
                cid = int(contratista_id)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'servicio_id y contratista_id deben ser números.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif servicio_id or contratista_id:
            return Response(
                {'error': 'Se requieren ambos parámetros servicio_id y contratista_id, o ninguno para campos globales.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if seccion == 'campos_formulario':
            if producto_id is not None:
                campos = get_campos_formulario_por_producto_id(sid, cid, producto_id)
            else:
                base = _get_campos_base_campos_formulario(sid, cid)
                campos = _filtrar_campos_por_contexto(list(base), sid, cid, None)
        else:
            if not servicio_id and not contratista_id:
                campos = get_campos_formulario(None, None, producto, solo_sin_producto, seccion)
            else:
                campos = get_campos_formulario(sid, cid, producto, solo_sin_producto, seccion)

        serializer = FormularioCampoSerializer(campos, many=True)
        return Response(serializer.data)
