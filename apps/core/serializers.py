from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
