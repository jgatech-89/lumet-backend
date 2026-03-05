"""
Serializers del módulo auth. Validación de entrada; sin lógica de negocio.
"""
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Validación de correo y contraseña para login."""
    correo = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class VerificarCodigoSerializer(serializers.Serializer):
    """Validación de correo y código de verificación."""
    correo = serializers.EmailField(write_only=True)
    codigo = serializers.CharField(write_only=True, max_length=10, min_length=6)


class ResendCodeSerializer(serializers.Serializer):
    """Validación de correo para reenviar código."""
    correo = serializers.EmailField(write_only=True)
