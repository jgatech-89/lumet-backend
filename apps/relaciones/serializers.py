"""
Serializers para la app relaciones.
"""
from rest_framework import serializers
from .models import Relacion


class RelacionSerializer(serializers.ModelSerializer):
    """Serializer completo con todos los campos del modelo Relacion."""

    class Meta:
        model = Relacion
        fields = [
            'id',
            'origen_tipo',
            'origen_id',
            'destino_tipo',
            'destino_id',
            'tipo_relacion',
            'estado',
            'created_at',
        ]
        read_only_fields = ['created_at']


class RelacionSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer reducido con solo destino_tipo y destino_id.
    Uso: selects dependientes en el frontend.
    """

    class Meta:
        model = Relacion
        fields = ['destino_tipo', 'destino_id']


class OpcionDestinoSerializer(serializers.Serializer):
    """
    Respuesta del endpoint /opciones/: lista de destinos con id, tipo y label.
    id = destino_id, tipo = destino_tipo, label = nombre de la entidad (para selects).
    """
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    label = serializers.CharField(allow_blank=True, required=False)
