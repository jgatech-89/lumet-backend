from rest_framework import serializers
from .models import Producto


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados (tablas)."""
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'estado', 'estado_producto']

    def get_estado(self, obj):
        return 'Activo' if obj.estado_producto == '1' else 'Inactivo'


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer completo para crear, actualizar y detalle."""

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'estado',
            'estado_producto',
            'fecha_registra',
            'usuario_registra',
            'updated_at',
            'updated_by',
            'fecha_elimina',
            'usuario_elimina',
        ]
        read_only_fields = [
            'fecha_registra',
            'usuario_registra',
            'updated_at',
            'updated_by',
            'fecha_elimina',
            'usuario_elimina',
        ]

    def validate_nombre(self, value):
        """Evita duplicados entre productos no eliminados."""
        queryset = Producto.objects.filter(nombre__iexact=value.strip(), fecha_elimina__isnull=True)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ya existe un producto con este nombre.')
        return value.strip()
