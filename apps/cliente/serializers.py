from rest_framework import serializers
from apps.servicio.models import Servicio
from apps.formularios.services import get_campos_formulario
from .models import Cliente, FormularioCliente, HistorialEstadoVenta


class FormularioClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioCliente
        fields = ['nombre_campo', 'respuesta_campo']


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
            'correo',
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
    """Serializer para detalle con respuestas del formulario y servicio_empresa_id."""
    respuestas = FormularioClienteSerializer(source='respuestas_formulario', many=True, read_only=True)
    servicio_empresa_id = serializers.SerializerMethodField()

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['respuestas', 'servicio_empresa_id']

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
    correo = serializers.EmailField(required=False, allow_blank=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list
    )

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
                    defaults={'respuesta_campo': respuesta_campo, 'usuario_registra': user}
                )
                if not created and fc.respuesta_campo != respuesta_campo:
                    fc.respuesta_campo = respuesta_campo
                    fc.save()
        return instance


def _cambiar_estado_venta(cliente, nuevo_estado, user):
    """Desactiva el estado anterior y crea uno nuevo en HistorialEstadoVenta."""
    HistorialEstadoVenta.objects.filter(cliente=cliente, activo=True).update(activo=False)
    HistorialEstadoVenta.objects.create(
        cliente=cliente,
        estado=nuevo_estado or 'venta_iniciada',
        activo=True,
        usuario_registra=user,
    )


class ClienteCreateSerializer(serializers.Serializer):
    """Serializer para crear cliente + respuestas del formulario en una sola petición."""
    servicio_id = serializers.IntegerField()
    producto = serializers.CharField(max_length=255, required=False, allow_blank=True)
    nombre = serializers.CharField(max_length=255)
    tipo_identificacion = serializers.CharField(max_length=10, required=False, allow_blank=True)
    numero_identificacion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    correo = serializers.EmailField(required=False, allow_blank=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list
    )

    def validate(self, attrs):
        """Valida que las respuestas correspondan a los campos del formulario del servicio y producto seleccionados."""
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
        NOMBRES_PRODUCTO_CAMPO = ['producto', 'Producto']
        NOMBRES_CAMBIO_TITULAR = ['cambio de titular', 'Cambio de titular', 'cambio titular', 'Cambio titular']
        NOMBRES_EXTRA_PERMITIDOS = ['vendedor', 'Vendedor']
        norm = lambda s: (s or '').lower().replace(' ', '_')
        es_campo_producto = lambda n: any(norm(n) == norm(p) for p in NOMBRES_PRODUCTO_CAMPO)
        es_extra_permitido = lambda n: any(norm(n) == norm(p) for p in NOMBRES_EXTRA_PERMITIDOS)

        def es_visible_si_cambio_titular(campo):
            vs = (getattr(campo, 'visible_si', None) or '').lower().replace('_', ' ').strip()
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
            campos_requeridos.add(c.nombre)

        for nombre_campo in respuestas_por_campo:
            if nombre_campo not in nombres_campos and not es_extra_permitido(nombre_campo):
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre_campo}" no está configurado para este servicio.'
                })

        for nombre in campos_requeridos:
            valor = respuestas_por_campo.get(nombre, '')
            if not valor or not str(valor).strip():
                raise serializers.ValidationError({
                    'respuestas': f'El campo "{nombre}" es obligatorio.'
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
        norm = lambda s: (s or '').lower().replace(' ', '_')
        estado_inicial = 'venta_iniciada'

        for item in respuestas:
            nombre_campo = item.get('nombre_campo', '')
            respuesta_campo = item.get('respuesta_campo', '')
            if any(norm(nombre_campo) == norm(n) for n in NOMBRES_ESTADO_VENTA):
                estado_inicial = (respuesta_campo or '').strip() or estado_inicial or 'venta_iniciada'
            else:
                FormularioCliente.objects.create(
                    cliente=cliente,
                    nombre_campo=nombre_campo,
                    respuesta_campo=str(respuesta_campo),
                    usuario_registra=user
                )

        HistorialEstadoVenta.objects.create(
            cliente=cliente,
            estado=estado_inicial,
            activo=True,
            usuario_registra=user,
        )
        return cliente
