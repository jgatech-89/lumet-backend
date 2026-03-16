from rest_framework import serializers
from .models import Contratista


def _nombre_persona(persona):
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


class ContratistaSerializer(serializers.ModelSerializer):
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
        model = Contratista
        fields = [
            'id',
            'nombre',
            'estado',
            'estado_contratista',
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

    def get_usuario_registra_nombre(self, obj):
        return _nombre_persona(obj.usuario_registra)

    def get_usuario_edita_nombre(self, obj):
        return _nombre_persona(obj.usuario_edita)

    def get_usuario_elimina_nombre(self, obj):
        return _nombre_persona(obj.usuario_elimina)

    def validate_nombre(self, value):
        """No permitir nombre duplicado entre contratistas activos (estado=1)."""
        nombre = (value or '').strip()
        if not nombre:
            return value
        qs = Contratista.objects.filter(nombre__iexact=nombre, estado='1')
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un contratista activo con este nombre.')
        return value
