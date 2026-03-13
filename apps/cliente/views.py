import io
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .models import Cliente, FormularioCliente, HistorialEstadoVenta
from .serializers import (
    ClienteSerializer,
    ClienteCreateSerializer,
    ClienteDetalleSerializer,
    ClienteUpdateSerializer,
    ClienteAgregarProductoSerializer,
    _cambiar_estado_venta,
)
from .filters import ClienteFilter


def _estado_venta_cliente(cliente):
    h = cliente.historial_estados_venta.filter(activo=True).first()
    return h.estado if h else 'venta_iniciada'


def _vendedor_nombre_cliente(cliente):
    from apps.persona.models import Vendedor
    r = cliente.respuestas_formulario.filter(nombre_campo__iexact='vendedor').first()
    if not r or not r.respuesta_campo:
        return None
    try:
        v = Vendedor.objects.filter(fecha_elimina__isnull=True).get(id=int(r.respuesta_campo))
        return v.nombre_completo
    except (ValueError, Vendedor.DoesNotExist):
        return r.respuesta_campo


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ClienteFilter
    search_fields = ['nombre', 'numero_identificacion', 'correo', 'telefono']

    def get_queryset(self):
        qs = Cliente.objects.filter(estado='1').order_by('-fecha_registro')
        if self.action == 'retrieve':
            qs = qs.prefetch_related('respuestas_formulario', 'historial_estados_venta')
        else:
            qs = qs.prefetch_related('respuestas_formulario', 'historial_estados_venta')
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteDetalleSerializer
        if self.action in ('update', 'partial_update'):
            return ClienteUpdateSerializer
        return ClienteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estado = '0'
        instance.usuario_elimina = request.user
        instance.fecha_elimina = timezone.now()
        instance.save()
        return Response(
            {'mensaje': 'Cliente eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = ClienteCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()
        return Response(
            {
                'mensaje': 'Cliente creado exitosamente.',
                'data': ClienteSerializer(cliente).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ClienteUpdateSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'mensaje': 'Cliente actualizado correctamente.',
            'data': ClienteDetalleSerializer(instance).data,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='agregar-producto')
    def agregar_producto(self, request, pk=None):
        """Agrega un nuevo producto a un cliente existente (sin duplicar datos del cliente)."""
        cliente = self.get_object()
        serializer = ClienteAgregarProductoSerializer(
            data=request.data,
            context={'request': request, 'cliente': cliente}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'mensaje': 'Producto agregado correctamente.'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de venta del cliente. Desactiva el anterior y crea uno nuevo."""
        cliente = self.get_object()
        nuevo_estado = (request.data.get('estado') or '').strip() or 'pendiente'
        _cambiar_estado_venta(cliente, nuevo_estado, request.user)
        return Response({
            'mensaje': 'Estado actualizado correctamente.',
            'estado': nuevo_estado,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        """Genera PDF con espacio de contrato con toda la información general del cliente."""
        cliente = self.get_object()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph('ESPACIO DE CONTRATO', ParagraphStyle('title', parent=styles['Heading1'], fontSize=16, spaceAfter=20)))
        elements.append(Spacer(1, 12))

        datos = [
            ['Nombre', cliente.nombre or '-'],
            ['Tipo identificación', cliente.tipo_identificacion or '-'],
            ['Número identificación', cliente.numero_identificacion or '-'],
            ['Teléfono', cliente.telefono or '-'],
            ['Correo', cliente.correo or '-'],
            ['Estado de venta', _estado_venta_cliente(cliente) or '-'],
            ['Vendedor', _vendedor_nombre_cliente(cliente) or '-'],
        ]
        for r in cliente.respuestas_formulario.all():
            datos.append([r.nombre_campo, r.respuesta_campo or '-'])

        t = Table(datos, colWidths=[4*cm, 12*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (0, -1), (0.2, 0.2, 0.2)),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, (0.7, 0.7, 0.7)),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 40))
        elements.append(Paragraph('Espacio reservado para condiciones del contrato y firmas.', ParagraphStyle('note', parent=styles['Normal'], fontSize=9, textColor=(0.5, 0.5, 0.5))))

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cliente_{cliente.id}_{cliente.nombre or "contrato"}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request):
        """Exporta clientes a Excel (.xlsx)."""
        queryset = self.filter_queryset(self.get_queryset())
        wb = Workbook()
        ws = wb.active
        ws.title = 'Clientes'
        headers = [
            'ID', 'Nombre', 'Tipo identificación', 'Número identificación', 'Teléfono', 'Correo',
            'Estado venta', 'Vendedor', 'Servicio ID'
        ]
        ws.append(headers)
        for c in queryset:
            ws.append([
                c.id, c.nombre or '', c.tipo_identificacion or '', c.numero_identificacion or '',
                c.telefono or '', c.correo or '', _estado_venta_cliente(c) or '',
                _vendedor_nombre_cliente(c) or '', c.servicio_id or ''
            ])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
        return response
