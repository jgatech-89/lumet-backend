from rest_framework import serializers
from .models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Persona
        fields = [
            'id',
            'username',
            'password',
            'tipo_identificacion',
            'identificacion',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'nombre_completo',
            'correo',
            'correo_auth',
            'telefono',
            'perfil',
            'estado',
            'verificado',
            'codigo_verificado',
            'is_active',
            'date_joined',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['nombre_completo', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        persona = super().create(validated_data)
        if password:
            persona.set_password(password)
            persona.save(update_fields=['password'])
        return persona

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
