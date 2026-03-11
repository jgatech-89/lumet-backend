from rest_framework import serializers
from apps.empresa.models import Empresa
from .models import Servicio


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


class ServicioSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.SerializerMethodField()
    empresa_id = serializers.PrimaryKeyRelatedField(
        queryset=Empresa.objects.filter(estado='1'),
        source='empresa',
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
        model = Servicio
        fields = [
            'id',
            'nombre',
            'estado',
            'estado_servicio',
            'empresa_id',
            'empresa_nombre',
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

    def get_empresa_nombre(self, obj):
        return obj.empresa.nombre if obj.empresa else None

    def get_usuario_registra_nombre(self, obj):
        return _nombre_persona(obj.usuario_registra)

    def get_usuario_edita_nombre(self, obj):
        return _nombre_persona(obj.usuario_edita)

    def get_usuario_elimina_nombre(self, obj):
        return _nombre_persona(obj.usuario_elimina)

    def validate(self, attrs):
        """
        No permitir mismo nombre en la misma empresa si ya existe un servicio ACTIVO (estado=1).
        Si existe uno inactivo (estado=0, eliminado lógicamente), sí se permite crear uno nuevo.
        """
        nombre = attrs.get('nombre')
        empresa = attrs.get('empresa')
        if not nombre or not empresa:
            return attrs
        qs = Servicio.objects.filter(
            nombre__iexact=nombre.strip(),
            empresa=empresa,
            estado='1',
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'nombre': 'Ya existe un servicio activo con este nombre en la empresa.',
            })
        return attrs
