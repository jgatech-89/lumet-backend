from rest_framework import serializers
from apps.servicio.models import Servicio
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
    servicio_nombre = serializers.SerializerMethodField()
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(estado='1'),
        source='servicio',
    )
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
            'servicio_id',
            'servicio_nombre',
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

    def get_servicio_nombre(self, obj):
        return obj.servicio.nombre if obj.servicio else None

    def get_usuario_registra_nombre(self, obj):
        return _nombre_persona(obj.usuario_registra)

    def get_usuario_edita_nombre(self, obj):
        return _nombre_persona(obj.usuario_edita)

    def get_usuario_elimina_nombre(self, obj):
        return _nombre_persona(obj.usuario_elimina)

    def validate(self, attrs):
        """
        No permitir mismo nombre en el mismo servicio si ya existe un contratista ACTIVO (estado=1).
        """
        nombre = attrs.get('nombre')
        servicio = attrs.get('servicio')
        if not nombre or not servicio:
            return attrs
        qs = Contratista.objects.filter(
            nombre__iexact=nombre.strip(),
            servicio=servicio,
            estado='1',
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'nombre': 'Ya existe un contratista activo con este nombre en el servicio.',
            })
        return attrs
