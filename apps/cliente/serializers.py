import re
from rest_framework import serializers
from apps.servicio.models import Servicio
from apps.formularios.services import get_campos_formulario
from .models import Cliente, FormularioCliente, HistorialEstadoVenta, ClienteEmpresa


def _validar_correo_o_carta(val):
    """Acepta: email válido, 'carta', 'papel'. No permite otros textos."""
    if not val or not str(val).strip():
        return True
    v = str(val).strip().lower()
    if v == 'carta' or v == 'papel':
        return True
    email_re = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_re.match(v))


def _validar_cuenta_bancaria(val):
    """Mínimo 22 números y 2 letras."""
    if not val or not str(val).strip():
        return True
    s = str(val).strip()
    nums = sum(1 for c in s if c.isdigit())
    lets = sum(1 for c in s if c.isalpha())
    return nums >= 22 and lets >= 2


class FormularioClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioCliente
        fields = ['nombre_campo', 'respuesta_campo']


def _vendedor_nombre_por_cliente_empresa(cliente_empresa):
    """Vendedor para un producto (ClienteEmpresa): historial activo, legacy o usuario_registra del ce."""
    if not cliente_empresa:
        return None
    h = HistorialEstadoVenta.objects.filter(
        cliente_empresa_id=cliente_empresa.pk,
        activo=True,
        estado_registro='1',
    ).select_related('usuario_registra').order_by('-fecha_registra').first()
    if h and h.usuario_registra_id:
        p = h.usuario_registra
        return getattr(p, 'nombre_completo', None) or (f'{getattr(p, "first_name", "")} {getattr(p, "last_name", "")}'.strip()) or str(p)
    h_legacy = HistorialEstadoVenta.objects.filter(
        cliente_id=cliente_empresa.cliente_id,
        cliente_empresa__isnull=True,
        activo=True,
        estado_registro='1',
    ).select_related('usuario_registra').order_by('-fecha_registra').first()
    if h_legacy and h_legacy.usuario_registra_id:
        p = h_legacy.usuario_registra
        return getattr(p, 'nombre_completo', None) or (f'{getattr(p, "first_name", "")} {getattr(p, "last_name", "")}'.strip()) or str(p)
    if cliente_empresa.usuario_registra_id:
        p = cliente_empresa.usuario_registra
        if p:
            return getattr(p, 'nombre_completo', None) or (f'{getattr(p, "first_name", "")} {getattr(p, "last_name", "")}'.strip()) or str(p)
    return None


class ClienteEmpresaSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    cerrador_nombre = serializers.SerializerMethodField()
    estado_venta = serializers.SerializerMethodField()
    respuestas = serializers.SerializerMethodField()

    class Meta:
        model = ClienteEmpresa
        fields = ['id', 'tipo_cliente', 'empresa', 'empresa_nombre', 'servicio', 'servicio_nombre', 'producto', 'vendedor', 'vendedor_nombre', 'cerrador', 'cerrador_nombre', 'estado_venta', 'fecha_registra', 'respuestas']

    def get_cerrador_nombre(self, obj):
        if obj.cerrador_id and obj.cerrador:
            return getattr(obj.cerrador, 'nombre_completo', None) or str(obj.cerrador)
        return ''

    def get_vendedor_nombre(self, obj):
        """Vendedor del producto: prioridad ClienteEmpresa.vendedor, luego fallbacks por historial/legacy."""
        if obj.vendedor_id and obj.vendedor:
            return getattr(obj.vendedor, 'nombre_completo', None) or str(obj.vendedor)
        return _vendedor_nombre_por_cliente_empresa(obj) or ''

    def get_estado_venta(self, obj):
        h = HistorialEstadoVenta.objects.filter(
            cliente_empresa=obj, activo=True, estado_registro='1'
        ).first()
        if h:
            return h.estado
        h_legacy = HistorialEstadoVenta.objects.filter(
            cliente=obj.cliente, cliente_empresa__isnull=True, activo=True, estado_registro='1'
        ).first()
        return h_legacy.estado if h_legacy else 'venta_iniciada'

    def get_respuestas(self, obj):
        """Solo respuestas de FormularioCliente filtradas por cliente_empresa_id."""
        return list(
            FormularioCliente.objects.filter(
                cliente_empresa_id=obj.id,
                estado='1',
            )
            .order_by('nombre_campo')
            .values('nombre_campo', 'respuesta_campo')
        )


class ClienteEmpresaSinRespuestasSerializer(serializers.ModelSerializer):
    """
    Igual que ClienteEmpresaSerializer pero sin respuestas.
    Usado en el detalle del cliente al abrir desde la tabla principal (ojito), para no cargar respuestas hasta que se abra el detalle de un producto.
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    cerrador_nombre = serializers.SerializerMethodField()
    estado_venta = serializers.SerializerMethodField()

    class Meta:
        model = ClienteEmpresa
        fields = ['id', 'tipo_cliente', 'empresa', 'empresa_nombre', 'servicio', 'servicio_nombre', 'producto', 'vendedor', 'vendedor_nombre', 'cerrador', 'cerrador_nombre', 'estado_venta', 'fecha_registra']

    def get_cerrador_nombre(self, obj):
        if obj.cerrador_id and obj.cerrador:
            return getattr(obj.cerrador, 'nombre_completo', None) or str(obj.cerrador)
        return ''

    def get_vendedor_nombre(self, obj):
        if obj.vendedor_id and obj.vendedor:
            return getattr(obj.vendedor, 'nombre_completo', None) or str(obj.vendedor)
        return _vendedor_nombre_por_cliente_empresa(obj) or ''

    def get_estado_venta(self, obj):
        h = HistorialEstadoVenta.objects.filter(
            cliente_empresa=obj, activo=True, estado_registro='1'
        ).first()
        if h:
            return h.estado
        h_legacy = HistorialEstadoVenta.objects.filter(
            cliente=obj.cliente, cliente_empresa__isnull=True, activo=True, estado_registro='1'
        ).first()
        return h_legacy.estado if h_legacy else 'venta_iniciada'


class ClienteMinimalSerializer(serializers.ModelSerializer):
    """Solo campos necesarios para el modal de detalle de un producto (ojito)."""
    vendedor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'vendedor_nombre']

    def get_vendedor_nombre(self, obj):
        from apps.persona.models import Vendedor
        r = obj.respuestas_formulario.filter(nombre_campo__iexact='vendedor').first()
        if not r or not r.respuesta_campo:
            return None
        try:
            v = Vendedor.objects.filter(fecha_elimina__isnull=True).get(id=int(r.respuesta_campo))
            return v.nombre_completo
        except (ValueError, Vendedor.DoesNotExist):
            return r.respuesta_campo


class ClienteEmpresaDetalleModalSerializer(serializers.ModelSerializer):
    """
    Solo los campos que usa el modal de detalle del producto (ojito).
    Omite id del producto, IDs de relaciones y fecha_registra.
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    cerrador_nombre = serializers.SerializerMethodField()
    estado_venta = serializers.SerializerMethodField()
    respuestas = serializers.SerializerMethodField()

    class Meta:
        model = ClienteEmpresa
        fields = ['producto', 'empresa_nombre', 'servicio_nombre', 'tipo_cliente', 'estado_venta', 'vendedor_nombre', 'cerrador_nombre', 'respuestas']

    def get_cerrador_nombre(self, obj):
        if obj.cerrador_id and obj.cerrador:
            return getattr(obj.cerrador, 'nombre_completo', None) or str(obj.cerrador)
        return ''

    def get_vendedor_nombre(self, obj):
        if obj.vendedor_id and obj.vendedor:
            return getattr(obj.vendedor, 'nombre_completo', None) or str(obj.vendedor)
        return _vendedor_nombre_por_cliente_empresa(obj) or ''

    def get_estado_venta(self, obj):
        h = HistorialEstadoVenta.objects.filter(
            cliente_empresa=obj, activo=True, estado_registro='1'
        ).first()
        if h:
            return h.estado
        h_legacy = HistorialEstadoVenta.objects.filter(
            cliente=obj.cliente, cliente_empresa__isnull=True, activo=True, estado_registro='1'
        ).first()
        return h_legacy.estado if h_legacy else 'venta_iniciada'

    def get_respuestas(self, obj):
        return list(
            FormularioCliente.objects.filter(
                cliente_empresa_id=obj.id,
                estado='1',
            )
            .order_by('nombre_campo')
            .values('nombre_campo', 'respuesta_campo')
        )


class ClienteSerializer(serializers.ModelSerializer):
    estado_venta = serializers.SerializerMethodField()
    vendedor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'tipo_identificacion',
            'numero_identificacion',
            'telefono',
            'correo_electronico_o_carta',
            'direccion',
            'cuenta_bancaria',
            'compania_anterior',
            'compania_actual',
            'documento_dni',
            'documento_factura',
            'creado_por_carga_masiva',
            'estado',
            'estado_venta',
            'vendedor_nombre',
            'servicio_id',
            'producto',
            'usuario_registra',
            'fecha_registro',
            'usuario_elimina',
            'fecha_elimina',
        ]
        read_only_fields = ['usuario_registra', 'usuario_elimina', 'fecha_registro', 'fecha_elimina']

    def get_estado_venta(self, obj):
        h = obj.historial_estados_venta.filter(activo=True).first()
        return h.estado if h else 'venta_iniciada'

    def get_vendedor_nombre(self, obj):
        from apps.persona.models import Vendedor
        r = obj.respuestas_formulario.filter(nombre_campo__iexact='vendedor').first()
        if not r or not r.respuesta_campo:
            return None
        try:
            v = Vendedor.objects.filter(fecha_elimina__isnull=True).get(id=int(r.respuesta_campo))
            return v.nombre_completo
        except (ValueError, Vendedor.DoesNotExist):
            return r.respuesta_campo


class ClienteDetalleSerializer(ClienteSerializer):
    """Serializer para detalle al abrir desde la tabla principal (ojito). cliente_empresas sin respuestas; las respuestas por producto se cargan al abrir el detalle de cada producto."""
    respuestas = FormularioClienteSerializer(source='respuestas_formulario', many=True, read_only=True)
    servicio_empresa_id = serializers.SerializerMethodField()
    cliente_empresas = ClienteEmpresaSinRespuestasSerializer(many=True, read_only=True)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['respuestas', 'servicio_empresa_id', 'cliente_empresas']

    def get_servicio_empresa_id(self, obj):
        if obj.servicio_id:
            try:
                return Servicio.objects.get(id=obj.servicio_id).empresa_id
            except Servicio.DoesNotExist:
                return None
        return None


class ClienteUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar cliente y respuestas del formulario."""
    nombre = serializers.CharField(max_length=255, required=False)
    tipo_identificacion = serializers.CharField(max_length=10, required=False, allow_blank=True)
    numero_identificacion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    correo_electronico_o_carta = serializers.CharField(max_length=254, required=False, allow_blank=True)
    direccion = serializers.CharField(max_length=500, required=False, allow_blank=True)
    cuenta_bancaria = serializers.CharField(max_length=100, required=False, allow_blank=True)
    compania_anterior = serializers.CharField(max_length=255, required=False, allow_blank=True)
    compania_actual = serializers.CharField(max_length=255, required=False, allow_blank=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list
    )

    def validate(self, attrs):
        instance = self.instance
        numero_id = (attrs.get('numero_identificacion') or (instance.numero_identificacion if instance else '')).strip()
        if numero_id and len(numero_id) < 3:
            raise serializers.ValidationError({
                'numero_identificacion': 'El número de identificación debe tener mínimo 3 caracteres.'
            })
        correo = (attrs.get('correo_electronico_o_carta') or (instance.correo_electronico_o_carta if instance else '')).strip()
        if correo and not _validar_correo_o_carta(correo):
            raise serializers.ValidationError({
                'correo_electronico_o_carta': 'Debe ser un correo electrónico válido o la palabra "carta" o "papel".'
            })
        cuenta = (attrs.get('cuenta_bancaria') or (instance.cuenta_bancaria if instance else '')).strip()
        if cuenta and not _validar_cuenta_bancaria(cuenta):
            raise serializers.ValidationError({
                'cuenta_bancaria': 'La cuenta bancaria debe tener mínimo 22 números y 2 letras.'
            })
        if cuenta and instance:
            if Cliente.objects.filter(
                cuenta_bancaria__iexact=cuenta,
                estado='1',
                fecha_elimina__isnull=True,
            ).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({
                    'cuenta_bancaria': 'Ya existe un cliente con esta cuenta bancaria.'
                })
        return attrs

    def update(self, instance, validated_data):
        respuestas = validated_data.pop('respuestas', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        NOMBRES_ESTADO_VENTA = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        user = self.context['request'].user

        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            respuesta_campo = str(item.get('respuesta_campo', ''))
            if not nombre_campo:
                continue
            if any(norm(nombre_campo) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                _cambiar_estado_venta(instance, respuesta_campo.strip() or 'venta_iniciada', user)
            else:
                fc, created = FormularioCliente.objects.get_or_create(
                    cliente=instance,
                    nombre_campo=nombre_campo,
                    cliente_empresa=None,
                    defaults={'respuesta_campo': respuesta_campo, 'usuario_registra': user},
                )
                if not created and fc.respuesta_campo != respuesta_campo:
                    fc.respuesta_campo = respuesta_campo
                    fc.save()
        return instance


def _cambiar_estado_venta(cliente, nuevo_estado, user, cliente_empresa=None, usuario_registra=None):
    """
    Desactiva el estado anterior y crea uno nuevo en HistorialEstadoVenta.
    Si cliente_empresa está definido, el estado se asocia al producto. Si no, al cliente (legacy).
    usuario_registra: si se pasa (ej. vendedor asignado), se usa como usuario_registra del historial;
    si no, se usa user (quien hace la petición).
    """
    quien_registra = usuario_registra if usuario_registra is not None else user
    if cliente_empresa:
        HistorialEstadoVenta.objects.filter(
            cliente_empresa=cliente_empresa, activo=True
        ).update(activo=False)
        HistorialEstadoVenta.objects.create(
            cliente=cliente,
            cliente_empresa=cliente_empresa,
            estado=nuevo_estado or 'venta_iniciada',
            activo=True,
            usuario_registra=quien_registra,
        )
    else:
        HistorialEstadoVenta.objects.filter(
            cliente=cliente, cliente_empresa__isnull=True, activo=True
        ).update(activo=False)
        HistorialEstadoVenta.objects.create(
            cliente=cliente,
            cliente_empresa=None,
            estado=nuevo_estado or 'venta_iniciada',
            activo=True,
            usuario_registra=quien_registra,
        )


class ClienteCreateSerializer(serializers.Serializer):
    """Serializer para crear cliente + respuestas del formulario en una sola petición."""
    servicio_id = serializers.IntegerField(required=False, allow_null=True)
    producto = serializers.CharField(max_length=255, required=False, allow_blank=True)
    nombre = serializers.CharField(max_length=255)
    tipo_identificacion = serializers.CharField(max_length=10, required=False, allow_blank=True)
    numero_identificacion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    correo_electronico_o_carta = serializers.CharField(max_length=254, required=False, allow_blank=True)
    direccion = serializers.CharField(max_length=500, required=False, allow_blank=True)
    cuenta_bancaria = serializers.CharField(max_length=100, required=False, allow_blank=True)
    compania_anterior = serializers.CharField(max_length=255, required=False, allow_blank=True)
    compania_actual = serializers.CharField(max_length=255, required=False, allow_blank=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list
    )

    def validate(self, attrs):
        """Valida respuestas, correo, numero_identificacion, cuenta_bancaria y duplicados."""
        numero_id = (attrs.get('numero_identificacion') or '').strip()
        if numero_id and len(numero_id) < 3:
            raise serializers.ValidationError({
                'numero_identificacion': 'El número de identificación debe tener mínimo 3 caracteres.'
            })
        correo = (attrs.get('correo_electronico_o_carta') or '').strip()
        if correo and not _validar_correo_o_carta(correo):
            raise serializers.ValidationError({
                'correo_electronico_o_carta': 'Debe ser un correo electrónico válido o la palabra "carta" o "papel".'
            })
        cuenta = (attrs.get('cuenta_bancaria') or '').strip()
        if cuenta and not _validar_cuenta_bancaria(cuenta):
            raise serializers.ValidationError({
                'cuenta_bancaria': 'La cuenta bancaria debe tener mínimo 22 números y 2 letras.'
            })
        if cuenta and Cliente.objects.filter(
            cuenta_bancaria__iexact=cuenta,
            estado='1',
            fecha_elimina__isnull=True,
        ).exists():
            raise serializers.ValidationError({
                'cuenta_bancaria': 'Ya existe un cliente con esta cuenta bancaria.'
            })
        if numero_id and Cliente.objects.filter(
            numero_identificacion__iexact=numero_id,
            estado='1',
            fecha_elimina__isnull=True,
        ).exists():
            raise serializers.ValidationError({
                'numero_identificacion': 'Ya existe un cliente creado con este número de identificación.'
            })

        servicio_id = attrs.get('servicio_id')
        respuestas = attrs.get('respuestas', [])
        producto = (attrs.get('producto') or '').strip() or None

        if not servicio_id:
            return attrs

        try:
            servicio = Servicio.objects.get(id=servicio_id, estado='1')
        except Servicio.DoesNotExist:
            raise serializers.ValidationError({'servicio_id': 'Servicio no válido o inactivo.'})

        empresa_id = servicio.empresa_id
        campos = list(get_campos_formulario(empresa_id, servicio_id, producto))
        nombres_campos = {c.nombre for c in campos}
        respuestas_por_campo = {item.get('nombre_campo'): item.get('respuesta_campo', '') for item in respuestas if item.get('nombre_campo')}

        NOMBRES_TIPO_CLIENTE = ['tipo_cliente', 'Tipo de cliente', 'Tipo Cliente', 'tipo cliente']
        NOMBRES_ESTADO_VENTA = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        NOMBRES_PRODUCTO_CAMPO = ['producto', 'Producto', 'Productos', 'Tipo producto', 'tipo de producto', 'Tipo de Producto']
        NOMBRES_CAMBIO_TITULAR = ['cambio de titular', 'Cambio de titular', 'cambio titular', 'Cambio titular']
        NOMBRES_EXTRA_PERMITIDOS = ['vendedor', 'Vendedor', 'comercial', 'Comercial', 'cerrador', 'Cerrador']
        NOMBRES_CAMPO_MODELO_CLIENTE = []
        # Tipo cliente puede no venir en la importación Excel; no exigir como obligatorio en create
        NOMBRES_TIPO_CLIENTE_CAMPO = ['tipo_cliente', 'tipo de cliente', 'Tipo de cliente', 'Tipo Cliente', 'tipo cliente']
        # Vendedor puede no venir en la importación Excel; no exigir como obligatorio en create
        NOMBRES_VENDEDOR_CAMPO = ['vendedor', 'Vendedor', 'comercial', 'Comercial']
        NOMBRES_CERRADOR_CAMPO = ['cerrador', 'Cerrador']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        es_campo_producto = lambda n: any(norm(n) == norm(p) for p in NOMBRES_PRODUCTO_CAMPO)
        es_extra_permitido = lambda n: any(norm(n) == norm(p) for p in NOMBRES_EXTRA_PERMITIDOS)
        es_campo_modelo_cliente = lambda n: norm(n) in NOMBRES_CAMPO_MODELO_CLIENTE
        es_campo_tipo_cliente = lambda n: any(norm(n) == norm(p) for p in NOMBRES_TIPO_CLIENTE_CAMPO)
        es_campo_vendedor = lambda n: any(norm(n) == norm(p) for p in NOMBRES_VENDEDOR_CAMPO)
        es_campo_cerrador = lambda n: any(norm(n) == norm(p) for p in NOMBRES_CERRADOR_CAMPO)

        def get_valor_campo(nombre_requerido):
            """Obtiene el valor con búsqueda flexible (ej: Vendedor vs vendedor)."""
            if nombre_requerido in respuestas_por_campo:
                return respuestas_por_campo[nombre_requerido]
            for k, v in respuestas_por_campo.items():
                if norm(k) == norm(nombre_requerido):
                    return v
            if 'vendedor' in norm(nombre_requerido):
                for k, v in respuestas_por_campo.items():
                    if 'vendedor' in norm(k):
                        return v
            return ''

        def es_visible_si_cambio_titular(campo):
            vs = getattr(campo, 'visible_si', None)
            if vs and isinstance(vs, dict) and vs.get('repetir_segun'):
                return False
            vs = (vs or '').lower().replace('_', ' ').strip()
            return 'cambio' in vs and 'titular' in vs

        def cambio_titular_marcado():
            for n in NOMBRES_CAMBIO_TITULAR:
                for k, v in respuestas_por_campo.items():
                    if norm(k) == norm(n):
                        val = str(v or '').lower().strip()
                        return val in ('1', 'si', 'true', 'yes')
            return False

        ct_marcado = cambio_titular_marcado()
        campos_requeridos = set()
        for c in campos:
            if not c.requerido or es_campo_producto(c.nombre):
                continue
            if es_visible_si_cambio_titular(c) and not ct_marcado:
                continue
            if es_campo_modelo_cliente(c.nombre):
                continue
            if es_campo_tipo_cliente(c.nombre):
                continue
            if es_campo_vendedor(c.nombre):
                continue
            if 'mantenimiento' in norm(c.nombre) or 'mantenimiento_luz' in norm(c.nombre):
                continue
            if 'cups' in norm(c.nombre):
                continue
            if 'fibra' in norm(c.nombre):
                continue
            campos_requeridos.add(c.nombre)

        def _nombre_es_campo_repetido_valido(nombre_campo):
            """Permite 'linea adicional (1)', 'linea adicional (2)' cuando existe campo 'linea adicional (x)' o 'linea adicional' con repetir_segun."""
            for c in campos:
                vs = getattr(c, 'visible_si', None)
                if not vs or not isinstance(vs, dict) or not vs.get('repetir_segun'):
                    continue
                base = (c.nombre or '').strip()
                if not base:
                    continue
                base_lower = base.lower()
                if '(x)' in base_lower or '($)' in base_lower:
                    pat = '^' + re.sub(r'\([x$]\)', r'(\\d+)', re.escape(base), flags=re.I) + r'$'
                else:
                    # Campo sin (x): aceptar "Linea adicional (1)", "Linea adicional (2)", etc.
                    pat = '^' + re.escape(base) + r'\s*\((\d+)\)\s*$'
                if re.match(pat, (nombre_campo or '').strip(), re.I):
                    return True
            return False

        for nombre_campo in respuestas_por_campo:
            if (nombre_campo not in nombres_campos
                    and not es_extra_permitido(nombre_campo)
                    and not es_campo_modelo_cliente(nombre_campo)
                    and not _nombre_es_campo_repetido_valido(nombre_campo)):
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre_campo}" no está configurado para este servicio.'
                })

        # En importación Excel no validamos campos obligatorios del formulario (respuestas viene vacío)
        if not self.context.get('importar_excel'):
            for nombre in campos_requeridos:
                valor = get_valor_campo(nombre)
                if not valor or not str(valor).strip():
                    raise serializers.ValidationError({
                        'respuestas': f'El campo "{nombre}" es obligatorio.'
                    })

        # Validar CUPS: si contiene "cups" o "cup" y tiene valor, mínimo 16 dígitos y 4 letras
        for c in campos:
            if 'cups' not in norm(c.nombre) and 'cup' not in norm(c.nombre):
                continue
            valor = get_valor_campo(c.nombre)
            if not valor or not str(valor).strip():
                continue
            digitos = len(re.findall(r'\d', str(valor)))
            letras = len(re.findall(r'[a-zA-Z]', str(valor)))
            if digitos < 16 or letras < 4:
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{c.nombre}" (CUPS) debe tener mínimo 16 dígitos y 4 letras.'
                })

        return attrs

    def create(self, validated_data):
        respuestas = validated_data.pop('respuestas', [])
        producto = (validated_data.pop('producto', '') or '').strip()
        user = self.context['request'].user

        cliente = Cliente.objects.create(
            **validated_data,
            producto=producto,
            usuario_registra=user
        )

        NOMBRES_ESTADO_VENTA = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        NOMBRES_TIPO_CLIENTE = ['tipo_cliente', 'Tipo de cliente', 'Tipo Cliente', 'tipo cliente']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        estado_inicial = 'venta_iniciada'
        tipo_cliente_val = ''
        vendedor_id_val = None
        cerrador_id_val = None
        for item in respuestas:
            nombre = (item.get('nombre_campo') or '').strip()
            if any(norm(nombre) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                estado_inicial = (item.get('respuesta_campo') or '').strip() or estado_inicial or 'venta_iniciada'
            elif any(norm(nombre) == norm(n) for n in NOMBRES_TIPO_CLIENTE):
                tipo_cliente_val = str(item.get('respuesta_campo', '')).strip()
            elif ('vendedor' in norm(nombre) or 'comercial' in norm(nombre)) and 'cerrador' not in norm(nombre):
                try:
                    vendedor_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    pass
            elif 'cerrador' in norm(nombre):
                try:
                    cerrador_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    pass

        servicio = Servicio.objects.filter(id=cliente.servicio_id).first()
        empresa_id = servicio.empresa_id if servicio else None
        ce = ClienteEmpresa.objects.create(
            cliente=cliente,
            tipo_cliente=tipo_cliente_val,
            vendedor_id=vendedor_id_val,
            cerrador_id=cerrador_id_val,
            empresa_id=empresa_id,
            servicio_id=cliente.servicio_id,
            producto=producto or '',
            formulario_id=None,
            usuario_registra=user,
        )

        HistorialEstadoVenta.objects.create(
            cliente=cliente,
            cliente_empresa=ce,
            estado=estado_inicial,
            activo=True,
            usuario_registra=user,
        )

        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            respuesta_campo = item.get('respuesta_campo', '')
            if any(norm(nombre_campo) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                continue
            FormularioCliente.objects.create(
                cliente=cliente,
                cliente_empresa=ce,
                nombre_campo=nombre_campo,
                respuesta_campo=str(respuesta_campo),
                usuario_registra=user,
            )

        return cliente


class ClienteAgregarProductoSerializer(serializers.Serializer):
    """Serializer para agregar un nuevo producto a un cliente existente (sin duplicar datos del cliente)."""
    servicio_id = serializers.IntegerField()
    producto = serializers.CharField(max_length=255, required=False, allow_blank=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list
    )

    def validate(self, attrs):
        servicio_id = attrs.get('servicio_id')
        respuestas = attrs.get('respuestas', [])
        producto = (attrs.get('producto') or '').strip() or None

        if not servicio_id:
            return attrs

        try:
            servicio = Servicio.objects.get(id=servicio_id, estado='1')
        except Servicio.DoesNotExist:
            raise serializers.ValidationError({'servicio_id': 'Servicio no válido o inactivo.'})

        empresa_id = servicio.empresa_id
        campos = list(get_campos_formulario(empresa_id, servicio_id, producto))
        nombres_campos = {c.nombre for c in campos}
        respuestas_por_campo = {item.get('nombre_campo'): item.get('respuesta_campo', '') for item in respuestas if item.get('nombre_campo')}

        NOMBRES_TIPO_CLIENTE = ['tipo_cliente', 'Tipo de cliente', 'Tipo Cliente', 'tipo cliente']
        NOMBRES_ESTADO_VENTA = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        NOMBRES_PRODUCTO_CAMPO = ['producto', 'Producto', 'Productos', 'Tipo producto', 'tipo de producto', 'Tipo de Producto']
        NOMBRES_CAMBIO_TITULAR = ['cambio de titular', 'Cambio de titular', 'cambio titular', 'Cambio titular']
        NOMBRES_EXTRA_PERMITIDOS = ['vendedor', 'Vendedor', 'comercial', 'Comercial', 'cerrador', 'Cerrador']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        es_campo_producto = lambda n: any(norm(n) == norm(p) for p in NOMBRES_PRODUCTO_CAMPO)
        es_extra_permitido = lambda n: any(norm(n) == norm(p) for p in NOMBRES_EXTRA_PERMITIDOS)

        def es_visible_si_cambio_titular(campo):
            vs = getattr(campo, 'visible_si', None)
            if vs and isinstance(vs, dict) and vs.get('repetir_segun'):
                return False
            vs = (vs or '').lower().replace('_', ' ').strip()
            return 'cambio' in vs and 'titular' in vs

        def _nombre_es_campo_repetido_valido(nombre_campo):
            for c in campos:
                vs = getattr(c, 'visible_si', None)
                if not vs or not isinstance(vs, dict) or not vs.get('repetir_segun'):
                    continue
                base = (c.nombre or '').strip()
                if not base:
                    continue
                base_lower = base.lower()
                if '(x)' in base_lower or '($)' in base_lower:
                    pat = '^' + re.sub(r'\([x$]\)', r'(\\d+)', re.escape(base), flags=re.I) + r'$'
                else:
                    pat = '^' + re.escape(base) + r'\s*\((\d+)\)\s*$'
                if re.match(pat, (nombre_campo or '').strip(), re.I):
                    return True
            return False

        def cambio_titular_marcado():
            for n in NOMBRES_CAMBIO_TITULAR:
                for k, v in respuestas_por_campo.items():
                    if norm(k) == norm(n):
                        val = str(v or '').lower().strip()
                        return val in ('1', 'si', 'true', 'yes')
            return False

        es_campo_estado_venta = lambda n: any(norm(n) == norm(ev) for ev in NOMBRES_ESTADO_VENTA)
        ct_marcado = cambio_titular_marcado()
        campos_requeridos = set()
        for c in campos:
            if not c.requerido or es_campo_producto(c.nombre) or es_campo_estado_venta(c.nombre):
                continue
            if es_visible_si_cambio_titular(c) and not ct_marcado:
                continue
            if 'mantenimiento' in norm(c.nombre) or 'cups' in norm(c.nombre) or 'fibra' in norm(c.nombre):
                continue
            campos_requeridos.add(c.nombre)

        def get_valor_campo(nombre_requerido):
            """Obtiene el valor con búsqueda flexible (ej: Vendedor vs vendedor, Comercial = Vendedor)."""
            if nombre_requerido in respuestas_por_campo:
                return respuestas_por_campo[nombre_requerido]
            for k, v in respuestas_por_campo.items():
                if norm(k) == norm(nombre_requerido):
                    return v
            # Campo vendedor/comercial: el formulario puede llamarse "Vendedor" o "Comercial"
            if 'vendedor' in norm(nombre_requerido) or 'comercial' in norm(nombre_requerido):
                for k, v in respuestas_por_campo.items():
                    if 'vendedor' in norm(k) or 'comercial' in norm(k):
                        return v
            return ''

        for nombre_campo in respuestas_por_campo:
            if (nombre_campo not in nombres_campos
                    and not es_extra_permitido(nombre_campo)
                    and not _nombre_es_campo_repetido_valido(nombre_campo)):
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre_campo}" no está configurado para este servicio.'
                })

        for nombre in campos_requeridos:
            valor = get_valor_campo(nombre)
            if not valor or not str(valor).strip():
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre}" es obligatorio.'
                })

        # Validar CUPS: si contiene "cups" o "cup" y tiene valor, mínimo 16 dígitos y 4 letras
        for c in campos:
            if 'cups' not in norm(c.nombre) and 'cup' not in norm(c.nombre):
                continue
            valor = get_valor_campo(c.nombre)
            if not valor or not str(valor).strip():
                continue
            digitos = len(re.findall(r'\d', str(valor)))
            letras = len(re.findall(r'[a-zA-Z]', str(valor)))
            if digitos < 16 or letras < 4:
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{c.nombre}" (CUPS) debe tener mínimo 16 dígitos y 4 letras.'
                })

        return attrs

    def create(self, validated_data):
        cliente = self.context['cliente']
        respuestas = validated_data.pop('respuestas', [])
        producto = (validated_data.pop('producto', '') or '').strip()
        servicio_id = validated_data.get('servicio_id')
        user = self.context['request'].user

        NOMBRES_ESTADO_VENTA = ['estado_venta', 'Estado de venta', 'Estado venta', 'estado venta']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        estado_nuevo_producto = 'venta_iniciada'
        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            if any(norm(nombre_campo) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                estado_nuevo_producto = (item.get('respuesta_campo') or '').strip() or estado_nuevo_producto
                break

        servicio = Servicio.objects.filter(id=servicio_id).first()
        empresa_id = servicio.empresa_id if servicio else None
        NOMBRES_TIPO_CLIENTE = ['tipo_cliente', 'Tipo de cliente', 'Tipo Cliente', 'tipo cliente']
        tipo_cliente_val = ''
        vendedor_id_val = None
        cerrador_id_val = None
        for item in respuestas:
            nombre = (item.get('nombre_campo') or '').strip()
            if any(norm(nombre) == norm(n) for n in NOMBRES_TIPO_CLIENTE):
                tipo_cliente_val = str(item.get('respuesta_campo', '')).strip()
            elif ('vendedor' in norm(nombre) or 'comercial' in norm(nombre)) and 'cerrador' not in norm(nombre):
                try:
                    vendedor_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    pass
            elif 'cerrador' in norm(nombre):
                try:
                    cerrador_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    pass

        ce = ClienteEmpresa.objects.create(
            cliente=cliente,
            tipo_cliente=tipo_cliente_val,
            vendedor_id=vendedor_id_val,
            cerrador_id=cerrador_id_val,
            empresa_id=empresa_id,
            servicio_id=servicio_id,
            producto=producto or '',
            formulario_id=None,
            usuario_registra=user,
        )

        _cambiar_estado_venta(cliente, estado_nuevo_producto, user, cliente_empresa=ce)

        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            respuesta_campo = str(item.get('respuesta_campo', ''))
            if not nombre_campo:
                continue
            if any(norm(nombre_campo) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                pass  # ya manejado arriba con cliente_empresa
            else:
                fc, created = FormularioCliente.objects.get_or_create(
                    cliente_empresa=ce,
                    nombre_campo=nombre_campo,
                    defaults={'cliente': cliente, 'respuesta_campo': respuesta_campo, 'usuario_registra': user},
                )
                if not created and fc.respuesta_campo != respuesta_campo:
                    fc.respuesta_campo = respuesta_campo
                    fc.save()

        return ce


class ClienteActualizarProductoSerializer(serializers.Serializer):
    """Actualiza un producto (ClienteEmpresa) existente, incluido vendedor_id por producto."""
    cliente_empresa_id = serializers.IntegerField()
    tipo_cliente = serializers.CharField(required=False, allow_blank=True, default='')
    servicio_id = serializers.IntegerField(required=False, allow_null=True)
    producto = serializers.CharField(required=False, allow_blank=True, default='')
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list,
    )

    def validate_servicio_id(self, value):
        if value is None:
            return value
        try:
            Servicio.objects.get(id=value, estado='1')
        except Servicio.DoesNotExist:
            raise serializers.ValidationError('Servicio no válido o inactivo.')
        return value

    def validate(self, attrs):
        cliente = self.context.get('cliente')
        ce_id = attrs.get('cliente_empresa_id')
        if not cliente or not ce_id:
            return attrs
        try:
            ce = ClienteEmpresa.objects.get(pk=ce_id, cliente=cliente, estado='1')
        except ClienteEmpresa.DoesNotExist:
            raise serializers.ValidationError({'cliente_empresa_id': 'Producto no encontrado o no pertenece a este cliente.'})
        attrs['_ce'] = ce
        norm = lambda s: (s or '').lower().replace(' ', '_')
        for item in (attrs.get('respuestas') or []):
            nombre = (item.get('nombre_campo') or '').strip()
            if 'cups' not in norm(nombre) and 'cup' not in norm(nombre):
                continue
            valor = str(item.get('respuesta_campo', '')).strip()
            if not valor:
                continue
            digitos = len(re.findall(r'\d', valor))
            letras = len(re.findall(r'[a-zA-Z]', valor))
            if digitos < 16 or letras < 4:
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre}" (CUPS) debe tener mínimo 16 dígitos y 4 letras.'
                })
        return attrs

    def save(self, **kwargs):
        cliente = self.context['cliente']
        user = self.context['request'].user
        ce = self.validated_data.get('_ce')
        if not ce:
            raise serializers.ValidationError('Producto no encontrado.')
        norm = lambda s: (s or '').lower().replace(' ', '_')
        # Campos directos
        if 'tipo_cliente' in self.validated_data:
            ce.tipo_cliente = (self.validated_data.get('tipo_cliente') or '').strip()
        if 'servicio_id' in self.validated_data and self.validated_data['servicio_id'] is not None:
            servicio_id = self.validated_data['servicio_id']
            try:
                servicio = Servicio.objects.get(id=servicio_id, estado='1')
                ce.servicio_id = servicio.id
                ce.empresa_id = servicio.empresa_id
            except Servicio.DoesNotExist:
                pass
        if 'producto' in self.validated_data:
            ce.producto = (self.validated_data.get('producto') or '').strip()
        # Comercial (vendedor) y cerrador desde respuestas
        respuestas = self.validated_data.get('respuestas') or []
        vendedor_id_val = None
        cerrador_id_val = None
        user = self.context['request'].user
        es_admin = getattr(user, 'perfil', None) == 'admin' or getattr(user, 'is_superuser', False)
        for item in respuestas:
            nombre = (item.get('nombre_campo') or '').strip()
            if 'vendedor' in norm(nombre) and 'cerrador' not in norm(nombre):
                try:
                    vendedor_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    vendedor_id_val = None
            elif 'cerrador' in norm(nombre) and es_admin:
                try:
                    cerrador_id_val = int(str(item.get('respuesta_campo', '')).strip())
                except (ValueError, TypeError):
                    cerrador_id_val = None
        if es_admin:
            ce.vendedor_id = vendedor_id_val
            ce.cerrador_id = cerrador_id_val
        ce.save()
        # Resto de respuestas -> FormularioCliente asociadas a ESTE producto (cliente_empresa)
        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            respuesta_campo = str(item.get('respuesta_campo', ''))
            if not nombre_campo or ('vendedor' in norm(nombre_campo) or 'comercial' in norm(nombre_campo)) and 'cerrador' not in norm(nombre_campo) or 'cerrador' in norm(nombre_campo):
                continue
            fc, created = FormularioCliente.objects.get_or_create(
                cliente_empresa=ce,
                nombre_campo=nombre_campo,
                defaults={'cliente': cliente, 'respuesta_campo': respuesta_campo, 'usuario_registra': user},
            )
            if not created and fc.respuesta_campo != respuesta_campo:
                fc.respuesta_campo = respuesta_campo
                fc.save()
        return ce
