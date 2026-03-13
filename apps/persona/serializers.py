from rest_framework import serializers
from .models import Persona, Vendedor


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
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
        ]
        read_only_fields = ['nombre_completo', 'date_joined', 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']
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


class VendedorListSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Vendedor
        fields = ['id', 'nombre_completo', 'tipo_identificacion', 'numero_identificacion', 'estado', 'estado_vendedor']

    def get_estado(self, obj):
        return 'Activo' if obj.estado_vendedor == '1' else 'Inactivo'


class VendedorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendedor
        fields = [
            'id',
            'nombre_completo',
            'tipo_identificacion',
            'numero_identificacion',
            'estado',
            'estado_vendedor',
            'fecha_registra',
            'usuario_registra',
            'updated_at',
            'updated_by',
            'fecha_elimina',
            'usuario_elimina',
        ]
        read_only_fields = [
            'fecha_registra', 'usuario_registra',
            'updated_at', 'updated_by',
            'fecha_elimina', 'usuario_elimina',
        ]
        validators = []

    def validate(self, attrs):
        tipo = attrs.get('tipo_identificacion')
        numero = attrs.get('numero_identificacion')
        if self.instance:
            tipo = tipo if tipo is not None else self.instance.tipo_identificacion
            numero = numero if numero is not None else self.instance.numero_identificacion
        if tipo is not None and numero is not None:
            qs = Vendedor.objects.filter(
                fecha_elimina__isnull=True,
                tipo_identificacion=tipo,
                numero_identificacion=numero,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'numero_identificacion': 'Ya existe un vendedor activo con este tipo y número de identificación.'}
                )
        return attrs
