from rest_framework import serializers
from apps.servicio.models import Servicio
from apps.contratista.models import Contratista
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
    servicio_nombre = serializers.SerializerMethodField()
    contratista_nombre = serializers.SerializerMethodField()
    opciones = CampoOpcionNestedSerializer(many=True, read_only=True)

    def get_servicio_nombre(self, obj):
        # En UI se muestra en la columna "Servicio"
        return obj.servicio.nombre if obj.servicio else 'Todos los servicios'

    def get_contratista_nombre(self, obj):
        # En UI se muestra en la columna "Contratista"
        if obj.contratista:
            return obj.contratista.nombre
        if obj.servicio:
            return 'Todos los contratistas'
        return 'Todos los servicios y contratistas'

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'servicio',
            'servicio_nombre',
            'contratista',
            'contratista_nombre',
            'producto',
            'placeholder',
            'seccion',
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
    Si aplicar_todos_servicios=True: servicio_id y contratista_id quedan null (aplica a todo).
    Si aplicar_todos_contratistas=True (y servicio definido): contratista_id queda null (aplica a todos los contratistas del servicio).
    """
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(estado='1'),
        source='servicio',
        required=False,
        allow_null=True
    )
    aplicar_todos_servicios = serializers.BooleanField(write_only=True, required=False, default=False)
    aplicar_todos_contratistas = serializers.BooleanField(write_only=True, required=False, default=False)
    contratista_id = serializers.PrimaryKeyRelatedField(
        queryset=Contratista.objects.filter(estado='1'),
        source='contratista',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'servicio_id',
            'aplicar_todos_servicios',
            'aplicar_todos_contratistas',
            'contratista_id',
            'producto',
            'placeholder',
            'seccion',
            'orden',
            'visible_si',
            'requerido',
            'activo',
            'estado',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        aplicar_servicios = attrs.pop('aplicar_todos_servicios', False)
        aplicar_contratistas = attrs.pop('aplicar_todos_contratistas', False)
        if aplicar_servicios:
            attrs['servicio'] = None
            attrs['contratista'] = None
        else:
            if not attrs.get('servicio'):
                raise serializers.ValidationError({
                    'servicio_id': 'Seleccione un servicio o marque "Aplicar a todos los servicios".'
                })
            if aplicar_contratistas:
                attrs['contratista'] = None
            elif not attrs.get('contratista'):
                raise serializers.ValidationError({
                    'contratista_id': 'Seleccione un contratista o marque "Aplicar a todos los contratistas".'
                })
        return attrs


class FormularioCampoSerializer(serializers.ModelSerializer):
    """Respuesta ligera para GET /api/formulario/?servicio_id=&contratista_id="""
    opciones = serializers.SerializerMethodField()

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'placeholder',
            'seccion',
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
