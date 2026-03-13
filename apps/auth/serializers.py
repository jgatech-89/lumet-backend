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


# ─── Recuperación de contraseña ───

class ForgotPasswordRequestSerializer(serializers.Serializer):
    """Solicitar código de recuperación al correo."""
    correo = serializers.EmailField(write_only=True)


class ForgotPasswordVerifySerializer(serializers.Serializer):
    """Verificar código de recuperación y obtener token para cambiar contraseña."""
    correo = serializers.EmailField(write_only=True)
    codigo = serializers.CharField(write_only=True, max_length=10, min_length=6)


class ForgotPasswordSetSerializer(serializers.Serializer):
    """Establecer nueva contraseña con el token recibido tras verificar el código."""
    token = serializers.CharField(write_only=True)
    nueva_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=1)
    confirmacion = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=1)

    def validate(self, attrs):
        if attrs.get('nueva_password') != attrs.get('confirmacion'):
            raise serializers.ValidationError({'confirmacion': 'Las contraseñas no coinciden.'})
        return attrs
