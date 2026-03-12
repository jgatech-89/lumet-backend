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
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    opciones = CampoOpcionNestedSerializer(many=True, read_only=True)

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
            'placeholder',
            'orden',
            'help_text',
            'default_value',
            'visible_si',
            'requerido',
            'activo',
            'estado',
            'opciones',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
        ]
        read_only_fields = fields



class CampoWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura para Campo (sin opciones anidadas)."""
    empresa_id = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.filter(estado='1'), source='empresa')
    servicio_id = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.filter(estado='1'), source='servicio')

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'empresa_id',
            'servicio_id',
            'placeholder',
            'orden',
            'help_text',
            'default_value',
            'visible_si',
            'requerido',
            'activo',
            'estado',
        ]
        read_only_fields = ['id']


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
            'help_text',
            'default_value',
            'requerido',
            'opciones',
        ]

    def get_opciones(self, obj):
        if obj.tipo != 'select':
            return []
        opciones_activas = sorted(
            (o for o in obj.opciones.all() if o.activo),
            key=lambda o: (o.orden, o.id),
        )
        return [{'label': o.label, 'value': o.value} for o in opciones_activas]
