from rest_framework import serializers
from apps.empresa.models import Empresa
from apps.servicio.models import Servicio
from .models import Campo, CampoOpcion


class CampoOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoOpcion
        fields = ['id', 'campo', 'label', 'value', 'orden', 'activo']
        read_only_fields = ['id']


class CampoOpcionNestedSerializer(serializers.ModelSerializer):
    """Solo label y value para anidar en Campo (lectura)."""
    class Meta:
        model = CampoOpcion
        fields = ['id', 'label', 'value', 'orden']


class CampoReadSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Campo (incluye opciones y nombres de FKs)."""
    empresa_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.SerializerMethodField()

    def get_empresa_nombre(self, obj):
        # En UI se muestra en la columna "Servicio"
        # Si no hay empresa asociada (aplica a todos), mostramos "Todos los servicios".
        return obj.empresa.nombre if obj.empresa else 'Todos los servicios'
    opciones = CampoOpcionNestedSerializer(many=True, read_only=True)

    def get_servicio_nombre(self, obj):
        # En UI se muestra en la columna "Contratista"
        # - Si hay servicio concreto: su nombre.
        # - Si hay empresa pero no servicio: todos los contratistas de ese servicio.
        # - Si tampoco hay empresa (aplica global): todos los servicios y contratistas.
        if obj.servicio:
            return obj.servicio.nombre
        if obj.empresa:
            return 'Todos los contratistas'
        return 'Todos los servicios y contratistas'

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'empresa',
            'empresa_nombre',
            'servicio',
            'servicio_nombre',
            'producto',
            'placeholder',
            'orden',
            'visible_si',
            'requerido',
            'activo',
            'estado',
            'opciones',
            'fecha_registra',
            'usuario_registra',
            'updated_at',
            'updated_by',
            'fecha_elimina',
            'usuario_elimina',
        ]
        read_only_fields = fields



class CampoWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura para Campo (sin opciones anidadas).
    Si aplicar_todos_empresas=True: empresa_id y servicio_id quedan null (aplica a todo).
    Si aplicar_todos_servicios=True (y empresa definida): servicio_id queda null (aplica a todos los servicios de la empresa).
    """
    empresa_id = serializers.PrimaryKeyRelatedField(
        queryset=Empresa.objects.filter(estado='1'),
        source='empresa',
        required=False,
        allow_null=True
    )
    aplicar_todos_empresas = serializers.BooleanField(write_only=True, required=False, default=False)
    aplicar_todos_servicios = serializers.BooleanField(write_only=True, required=False, default=False)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(estado='1'),
        source='servicio',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'empresa_id',
            'aplicar_todos_empresas',
            'aplicar_todos_servicios',
            'servicio_id',
            'producto',
            'placeholder',
            'orden',
            'visible_si',
            'requerido',
            'activo',
            'estado',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        aplicar_empresas = attrs.pop('aplicar_todos_empresas', False)
        aplicar_servicios = attrs.pop('aplicar_todos_servicios', False)
        if aplicar_empresas:
            attrs['empresa'] = None
            attrs['servicio'] = None
        else:
            if not attrs.get('empresa'):
                raise serializers.ValidationError({
                    'empresa_id': 'Seleccione una empresa o marque "Aplicar a todas las empresas".'
                })
            if aplicar_servicios:
                attrs['servicio'] = None
            elif not attrs.get('servicio'):
                raise serializers.ValidationError({
                    'servicio_id': 'Seleccione un servicio o marque "Aplicar a todos los servicios".'
                })
        return attrs


class FormularioCampoSerializer(serializers.ModelSerializer):
    """Respuesta ligera para GET /api/formulario/?empresa_id=&servicio_id="""
    opciones = serializers.SerializerMethodField()

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'placeholder',
            'requerido',
            'visible_si',
            'opciones',
        ]

    def get_opciones(self, obj):
        if obj.tipo != 'select':
            return []
        opciones_activas = sorted(
            (o for o in obj.opciones.all() if o.activo and o.estado == '1'),
            key=lambda o: (o.orden, o.id),
        )
        return [{'label': o.label, 'value': o.value} for o in opciones_activas]
