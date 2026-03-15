from rest_framework import serializers
from .models import Servicio


class ServicioMinimalSerializer(serializers.ModelSerializer):
    """Solo id y nombre, para selectores (ej. modal añadir campo)."""
    class Meta:
        model = Servicio
        fields = ['id', 'nombre']


def _nombre_persona(persona):
    """
    Construye el nombre completo de la Persona concatenando:
    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido.
    Si todo está vacío, devuelve username como fallback.
    """
    if persona is None:
        return None
    partes = [
        persona.primer_nombre,
        persona.segundo_nombre,
        persona.primer_apellido,
        persona.segundo_apellido,
    ]
    nombre = ' '.join(p for p in partes if p).strip()
    if nombre:
        return nombre
    return persona.username or str(persona.pk)


class ServicioSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    usuario_registra_nombre = serializers.SerializerMethodField()
    usuario_edita_nombre = serializers.SerializerMethodField()
    usuario_elimina_nombre = serializers.SerializerMethodField()
    usuario_registra_id = serializers.PrimaryKeyRelatedField(
        source='usuario_registra', read_only=True, allow_null=True
    )
    usuario_edita_id = serializers.PrimaryKeyRelatedField(
        source='usuario_edita', read_only=True, allow_null=True
    )
    usuario_elimina_id = serializers.PrimaryKeyRelatedField(
        source='usuario_elimina', read_only=True, allow_null=True
    )

    class Meta:
        model = Servicio
        fields = [
            'id',
            'nombre',
            'estado',
            'estado_servicio',
            'usuario_registra_id',
            'usuario_registra_nombre',
            'usuario_edita_id',
            'usuario_edita_nombre',
            'usuario_elimina_id',
            'usuario_elimina_nombre',
            'fecha_registro',
            'fecha_edita',
            'fecha_elimina',
        ]
        read_only_fields = [
            'usuario_registra',
            'usuario_edita',
            'usuario_elimina',
            'fecha_registro',
            'fecha_edita',
            'fecha_elimina',
        ]

    def get_estado(self, obj):
        return 'Activa' if obj.estado_servicio == '1' else 'Inactiva'

    def get_usuario_registra_nombre(self, obj):
        return _nombre_persona(obj.usuario_registra)

    def get_usuario_edita_nombre(self, obj):
        return _nombre_persona(obj.usuario_edita)

    def get_usuario_elimina_nombre(self, obj):
        return _nombre_persona(obj.usuario_elimina)

    def validate_nombre(self, value):
        """Evita duplicados solo entre servicios no eliminados (estado=1)."""
        queryset = Servicio.objects.filter(nombre__iexact=value, estado='1')
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un servicio con este nombre.")
        return value