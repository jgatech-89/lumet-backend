import io
from django.http import HttpResponse
from django.db.models import Prefetch
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
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
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from .models import Cliente, FormularioCliente, HistorialEstadoVenta, ClienteEmpresa
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


def _empresa_servicio_producto_para_cliente(cliente):
    from apps.servicio.models import Servicio
    ce = next(iter(cliente.cliente_empresas.all()), None)
    if ce:
        return (
            (ce.empresa.nombre if ce.empresa else ''),
            (ce.servicio.nombre if ce.servicio else ''),
            ce.producto or '',
        )
    servicio = Servicio.objects.filter(id=cliente.servicio_id).select_related('empresa').first() if cliente.servicio_id else None
    empresa_nombre = servicio.empresa.nombre if servicio and servicio.empresa_id else ''
    servicio_nombre = servicio.nombre if servicio else ''
    producto = (cliente.producto or '').strip()
    return (empresa_nombre, servicio_nombre, producto)


def _formatear_estado_venta_legible(valor):
    if not valor or not str(valor).strip():
        return ''
    v = str(valor).strip().lower().replace('-', ' ')
    mapeo = {
        'venta_iniciada': 'Venta Iniciada',
        'venta iniciada': 'Venta Iniciada',
        'completada': 'Completada',
        'pendiente': 'Pendiente',
        'cancelada': 'Cancelada',
        'en_proceso': 'En Proceso',
        'en proceso': 'En Proceso',
    }
    if v in mapeo:
        return mapeo[v]
    return ' '.join(p.capitalize() for p in v.split('_') if p)


def _productos_para_pdf(cliente):
    from apps.servicio.models import Servicio
    empresas = list(cliente.cliente_empresas.all())
    if empresas:
        return [
            {
                'empresa_nombre': (ce.empresa.nombre if ce.empresa else '-'),
                'servicio_nombre': (ce.servicio.nombre if ce.servicio else '-'),
                'producto': ce.producto or '-',
                'tipo_cliente': ce.tipo_cliente or '-',
            }
            for ce in empresas
        ]
    servicio = Servicio.objects.filter(id=cliente.servicio_id).select_related('empresa').first() if cliente.servicio_id else None
    empresa_nombre = servicio.empresa.nombre if servicio and servicio.empresa_id else '-'
    servicio_nombre = servicio.nombre if servicio else '-'
    producto = (cliente.producto or '').strip() or '-'
    return [{'empresa_nombre': empresa_nombre, 'servicio_nombre': servicio_nombre, 'producto': producto, 'tipo_cliente': '-'}]


def _estilo_tabla_base():
    return [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]


def _formatear_estado_venta(valor):
    if not valor or not str(valor).strip():
        return '-'
    v = str(valor).strip().lower().replace('-', ' ')
    mapeo = {
        'venta_iniciada': 'VENTA INICIADA',
        'venta iniciada': 'VENTA INICIADA',
        'completada': 'COMPLETADA',
        'pendiente': 'PENDIENTE',
        'cancelada': 'CANCELADA',
        'en_proceso': 'EN PROCESO',
        'en proceso': 'EN PROCESO',
    }
    if v in mapeo:
        return mapeo[v]
    return ' '.join(p.upper() for p in v.split('_') if p)


def _formatear_valor_campo(nombre_campo, valor, estado_venta_formateado=None, vendedor_nombre=None):
    if valor is None:
        return '-'
    raw = str(valor).strip()
    norm_nombre = (nombre_campo or '').lower().replace(' ', '_').replace('-', ' ')
    if not raw and norm_nombre not in ('estado_venta', 'estado de venta', 'vendedor'):
        return '-'
    if 'estado' in norm_nombre and 'venta' in norm_nombre:
        if estado_venta_formateado is not None:
            return estado_venta_formateado
        return _formatear_estado_venta(raw)
    if norm_nombre == 'vendedor':
        if vendedor_nombre:
            return vendedor_nombre
        return raw if raw else '-'
    if 'cambio' in norm_nombre and 'titular' in norm_nombre:
        if raw.lower() in ('1', 'si', 'sí', 'true', 'yes', 'verdadero'):
            return 'Sí'
        if raw.lower() in ('0', 'no', 'false', 'none', ''):
            return 'No'
        return raw
    if raw in ('1', '0'):
        return 'Sí' if raw == '1' else 'No'
    return raw


def _formatear_etiqueta_campo(nombre_campo):
    if not nombre_campo:
        return '-'
    s = str(nombre_campo).strip()
    if s.lower() in ('cambio de titular', 'cambio titular'):
        return 'CAMBIO DE TITULAR'
    if '_' in s and ' ' not in s:
        return s.replace('_', ' ').upper()
    return s.upper()


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ClienteFilter
    search_fields = ['nombre', 'numero_identificacion', 'correo', 'telefono']

    def get_queryset(self):
        qs = Cliente.objects.filter(estado='1').order_by('-fecha_registro')
        prefetch = [
            'respuestas_formulario',
            'historial_estados_venta',
            Prefetch(
                'cliente_empresas',
                queryset=ClienteEmpresa.objects.filter(estado='1').select_related('empresa', 'servicio').order_by('id'),
            ),
        ]
        qs = qs.prefetch_related(*prefetch)
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
        """
        Cambia el estado de venta de un producto del cliente.
        Si cliente_empresa_id se envía, aplica a ese producto. Si no, usa el primer producto del cliente.
        """
        cliente = self.get_object()
        nuevo_estado = (request.data.get('estado') or '').strip() or 'pendiente'
        cliente_empresa_id = request.data.get('cliente_empresa_id')
        cliente_empresa = None
        if cliente_empresa_id:
            try:
                ce = ClienteEmpresa.objects.get(
                    id=cliente_empresa_id,
                    cliente=cliente,
                    estado='1',
                )
                cliente_empresa = ce
            except ClienteEmpresa.DoesNotExist:
                return Response(
                    {'error': 'Producto no encontrado o no pertenece a este cliente.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            ce = cliente.cliente_empresas.filter(estado='1').first()
            if ce:
                cliente_empresa = ce
        _cambiar_estado_venta(cliente, nuevo_estado, request.user, cliente_empresa=cliente_empresa)
        return Response({
            'mensaje': 'Estado actualizado correctamente.',
            'estado': nuevo_estado,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        cliente = self.get_object()
        productos = _productos_para_pdf(cliente)
        respuestas = sorted(
            [r for r in cliente.respuestas_formulario.all() if r.estado == '1'],
            key=lambda r: (r.nombre_campo or ''),
        )
        estado_venta_raw = _estado_venta_cliente(cliente)
        estado_venta = _formatear_estado_venta(estado_venta_raw) if estado_venta_raw else '-'
        vendedor = _vendedor_nombre_cliente(cliente) or '-'
        fecha_generacion = timezone.now().strftime('%d/%m/%Y %H:%M')

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.8 * cm,
            leftMargin=1.8 * cm,
            topMargin=1.8 * cm,
            bottomMargin=2.2 * cm,
        )
        styles = getSampleStyleSheet()
        color_titulo = colors.HexColor('#1e3a5f')
        color_seccion = colors.HexColor('#2c5282')
        color_etiqueta = colors.HexColor('#4a5568')
        color_valor = colors.HexColor('#2d3748')
        color_bg_etiqueta = colors.HexColor('#edf2f7')
        color_pie = colors.HexColor('#718096')

        def _pie_pagina(canvas, document):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(color_pie)
            w = document.pagesize[0]
            canvas.drawCentredString(w / 2, 1.2 * cm, f'Documento generado el {fecha_generacion}')
            canvas.restoreState()

        header_style = ParagraphStyle(
            'pdf_header',
            parent=styles['Normal'],
            fontSize=8,
            textColor=color_pie,
            spaceAfter=2,
            alignment=2,
        )
        title_style = ParagraphStyle(
            'pdf_title',
            parent=styles['Heading1'],
            fontSize=13,
            spaceBefore=0,
            spaceAfter=10,
            textColor=color_titulo,
            fontName='Helvetica-Bold',
        )
        section_style = ParagraphStyle(
            'pdf_section',
            parent=styles['Heading2'],
            fontSize=10,
            spaceBefore=16,
            spaceAfter=6,
            textColor=color_seccion,
            fontName='Helvetica-Bold',
        )
        note_style = ParagraphStyle(
            'pdf_note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=color_pie,
        )
        elements = []

        norm_campo = lambda s: (s or '').lower().strip().replace(' ', '_')
        respuestas_sin_vendedor = [r for r in respuestas if norm_campo(r.nombre_campo) != 'vendedor']

        for idx, prod in enumerate(productos):
            if idx > 0:
                elements.append(PageBreak())

            elements.append(Paragraph('DOCUMENTO CONFIDENCIAL', header_style))
            elements.append(Spacer(1, 4))

            titulo_producto = prod['producto'] if prod['producto'] != '-' else f'Producto {idx + 1}'
            elements.append(Paragraph(f'ESPACIO DE CONTRATO — {titulo_producto}', title_style))
            elements.append(Spacer(1, 14))

            # 1. DATOS DEL CLIENTE (sin vendedor)
            elements.append(Paragraph('1. DATOS DEL CLIENTE', section_style))
            datos_cliente = [
                ['NOMBRE', cliente.nombre or '-'],
                ['TIPO DE IDENTIFICACIÓN', cliente.tipo_identificacion or '-'],
                ['NÚMERO DE IDENTIFICACIÓN', cliente.numero_identificacion or '-'],
                ['TELÉFONO', cliente.telefono or '-'],
                ['CORREO ELECTRÓNICO', cliente.correo or '-'],
                ['ESTADO DE VENTA', estado_venta],
            ]
            t_cli = Table(datos_cliente, colWidths=[5 * cm, 10.5 * cm])
            t_cli.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), color_bg_etiqueta),
                ('TEXTCOLOR', (0, 0), (0, -1), color_etiqueta),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TEXTCOLOR', (1, 0), (1, -1), color_valor),
                * _estilo_tabla_base(),
            ]))
            elements.append(t_cli)

            # 2. EMPRESA Y PRODUCTO (relación cliente_empresas)
            elements.append(Paragraph('2. EMPRESA Y PRODUCTO ASOCIADO', section_style))
            datos_empresa = [
                ['EMPRESA', prod['empresa_nombre']],
                ['SERVICIO', prod['servicio_nombre']],
                ['PRODUCTO', prod['producto']],
                ['TIPO DE CLIENTE', prod['tipo_cliente']],
            ]
            t_emp = Table(datos_empresa, colWidths=[5 * cm, 10.5 * cm])
            t_emp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), color_bg_etiqueta),
                ('TEXTCOLOR', (0, 0), (0, -1), color_etiqueta),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TEXTCOLOR', (1, 0), (1, -1), color_valor),
                * _estilo_tabla_base(),
            ]))
            elements.append(t_emp)

            # 3. INFORMACIÓN DEL FORMULARIO (todos los campos excepto vendedor)
            elements.append(Paragraph('3. INFORMACIÓN DEL FORMULARIO', section_style))
            datos_form = [
                [
                    _formatear_etiqueta_campo(r.nombre_campo),
                    _formatear_valor_campo(
                        r.nombre_campo,
                        r.respuesta_campo,
                        estado_venta_formateado=estado_venta,
                        vendedor_nombre=None,
                    ),
                ]
                for r in respuestas_sin_vendedor
            ]
            if datos_form:
                t_form = Table(datos_form, colWidths=[5 * cm, 10.5 * cm])
                t_form.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), color_bg_etiqueta),
                    ('TEXTCOLOR', (0, 0), (0, -1), color_etiqueta),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('TEXTCOLOR', (1, 0), (1, -1), color_valor),
                    * _estilo_tabla_base(),
                ]))
                elements.append(t_form)
            else:
                elements.append(Paragraph('Sin respuestas de formulario registradas.', note_style))

            # 4. DATOS DEL VENDEDOR
            elements.append(Paragraph('4. DATOS DEL VENDEDOR', section_style))
            datos_vendedor = [
                ['VENDEDOR ASIGNADO', vendedor],
            ]
            t_vend = Table(datos_vendedor, colWidths=[5 * cm, 10.5 * cm])
            t_vend.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), color_bg_etiqueta),
                ('TEXTCOLOR', (0, 0), (0, -1), color_etiqueta),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TEXTCOLOR', (1, 0), (1, -1), color_valor),
                * _estilo_tabla_base(),
            ]))
            elements.append(t_vend)

        doc.build(elements, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        nombre_safe = (cliente.nombre or 'contrato').replace(' ', '_')[:50]
        response['Content-Disposition'] = f'attachment; filename="cliente_{cliente.id}_{nombre_safe}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request):
        """Exporta clientes a Excel: una fila por cada producto del cliente, todo en MAYÚSCULAS."""
        queryset = self.filter_queryset(self.get_queryset())
        wb = Workbook()
        ws = wb.active
        ws.title = 'Clientes'

        def _mayus(s):
            return (s or '').strip().upper() if isinstance(s, str) else str(s or '').upper()

        headers = [
            'NOMBRE', 'TIPO IDENTIFICACIÓN', 'NÚMERO IDENTIFICACIÓN', 'TELÉFONO', 'CORREO',
            'TIPO DE EMPRESA', 'TIPO DE PRODUCTO', 'TIPO DE SERVICIO',
            'ESTADO VENTA', 'VENDEDOR',
        ]
        ws.append(headers)

        for c in queryset:
            productos = _productos_para_pdf(c)
            estado_raw = _estado_venta_cliente(c)
            estado_venta = _formatear_estado_venta(estado_raw) if estado_raw else ''
            vendedor = _vendedor_nombre_cliente(c) or ''
            for prod in productos:
                ws.append([
                    _mayus(c.nombre),
                    _mayus(c.tipo_identificacion),
                    _mayus(c.numero_identificacion),
                    _mayus(c.telefono),
                    _mayus(c.correo),
                    _mayus(prod['empresa_nombre']),
                    _mayus(prod['producto']),
                    _mayus(prod['servicio_nombre']),
                    _mayus(estado_venta),
                    _mayus(vendedor),
                ])

        header_fill = PatternFill(start_color='1e3a5f', end_color='1e3a5f', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=11)
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin'),
        )
        for col, _ in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border

        column_widths = [22, 18, 20, 14, 28, 22, 22, 22, 16, 22]
        for col, width in enumerate(column_widths, start=1):
            ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = width

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center', wrap_text=True)

        ws.freeze_panes = 'A2'

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
        return response
