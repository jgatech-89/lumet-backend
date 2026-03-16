from rest_framework import serializers
from apps.servicio.models import Servicio
from apps.contratista.models import Contratista
from .models import Campo, CampoOpcion


def _detectar_ciclo_dependencia(campo_id, depende_de_id, campos_por_id):
    """Devuelve True si asignar depende_de_id a campo_id crea un ciclo."""
    if not depende_de_id or not campo_id:
        return False
    visitados = set()
    actual = depende_de_id
    while actual:
        if actual == campo_id:
            return True
        if actual in visitados:
            return False
        visitados.add(actual)
        padre = campos_por_id.get(actual)
        actual = padre.depende_de_id if padre and getattr(padre, 'depende_de_id', None) else None
    return False


class CampoOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoOpcion
        fields = ['id', 'campo', 'label', 'value', 'orden', 'activo']
        read_only_fields = ['id']


class CampoOpcionNestedSerializer(serializers.ModelSerializer):
    """Solo label y value para anidar en Campo (lectura)."""
    class Meta:
        model = CampoOpcion
        fields = ['id', 'label', 'value', 'orden']


class CampoReadSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Campo (incluye opciones y nombres de FKs)."""
    servicio_nombre = serializers.SerializerMethodField()
    contratista_nombre = serializers.SerializerMethodField()
    depende_de_nombre = serializers.SerializerMethodField()
    opciones = CampoOpcionNestedSerializer(many=True, read_only=True)

    def get_servicio_nombre(self, obj):
        # En UI se muestra en la columna "Servicio"
        return obj.servicio.nombre if obj.servicio else 'Todos los servicios'

    def get_contratista_nombre(self, obj):
        # En UI se muestra en la columna "Contratista"
        if obj.contratista:
            return obj.contratista.nombre
        if obj.servicio:
            return 'Todos los contratistas'
        return 'Todos los servicios y contratistas'

    def get_depende_de_nombre(self, obj):
        return obj.depende_de.nombre if obj.depende_de else None

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'entidad',
            'depende_de',
            'depende_de_nombre',
            'servicio',
            'servicio_nombre',
            'contratista',
            'contratista_nombre',
            'producto',
            'placeholder',
            'seccion',
            'orden',
            'visible_si',
            'requerido',
            'activo',
            'estado',
            'opciones',
            'fecha_registra',
            'usuario_registra',
            'updated_at',
            'updated_by',
            'fecha_elimina',
            'usuario_elimina',
        ]
        read_only_fields = fields



class CampoWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura para Campo (sin opciones anidadas).
    Si aplicar_todos_servicios=True: servicio_id y contratista_id quedan null (aplica a todo).
    Si aplicar_todos_contratistas=True (y servicio definido): contratista_id queda null (aplica a todos los contratistas del servicio).
    """
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(estado='1'),
        source='servicio',
        required=False,
        allow_null=True
    )
    aplicar_todos_servicios = serializers.BooleanField(write_only=True, required=False, default=False)
    aplicar_todos_contratistas = serializers.BooleanField(write_only=True, required=False, default=False)
    contratista_id = serializers.PrimaryKeyRelatedField(
        queryset=Contratista.objects.filter(estado='1'),
        source='contratista',
        required=False,
        allow_null=True
    )
    depende_de_id = serializers.PrimaryKeyRelatedField(
        queryset=Campo.objects.filter(fecha_elimina__isnull=True, estado='1'),
        source='depende_de',
        required=False,
        allow_null=True
    )

    entidad = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'entidad',
            'depende_de_id',
            'servicio_id',
            'aplicar_todos_servicios',
            'aplicar_todos_contratistas',
            'contratista_id',
            'producto',
            'placeholder',
            'seccion',
            'orden',
            'visible_si',
            'requerido',
            'activo',
            'estado',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        entidad = attrs.get('entidad')
        if tipo == 'entity_select':
            entidades_permitidas = ('servicio', 'contratista', 'producto', 'vendedor')
            if not entidad or not str(entidad).strip():
                raise serializers.ValidationError({
                    'entidad': 'Cuando el tipo es "Selector de entidad", debe elegir una entidad.'
                })
            if str(entidad).strip().lower() not in entidades_permitidas:
                raise serializers.ValidationError({
                    'entidad': f'Entidad no permitida. Debe ser una de: {", ".join(entidades_permitidas)}.'
                })
            attrs['entidad'] = str(entidad).strip().lower()
        else:
            attrs['entidad'] = None

        aplicar_servicios = attrs.pop('aplicar_todos_servicios', False)
        aplicar_contratistas = attrs.pop('aplicar_todos_contratistas', False)
        if aplicar_servicios:
            attrs['servicio'] = None
            attrs['contratista'] = None
        else:
            if not attrs.get('servicio'):
                raise serializers.ValidationError({
                    'servicio_id': 'Seleccione un servicio o marque "Aplicar a todos los servicios".'
                })
            if aplicar_contratistas:
                attrs['contratista'] = None
            elif not attrs.get('contratista'):
                raise serializers.ValidationError({
                    'contratista_id': 'Seleccione un contratista o marque "Aplicar a todos los contratistas".'
                })

        depende_de = attrs.get('depende_de')
        instance = self.instance
        seccion = attrs.get('seccion') or (instance.seccion if instance else None)
        if depende_de:
            if instance and instance.pk == depende_de.pk:
                raise serializers.ValidationError({
                    'depende_de_id': 'Un campo no puede depender de sí mismo.'
                })
            if seccion and depende_de.seccion != seccion:
                raise serializers.ValidationError({
                    'depende_de_id': 'El campo del que depende debe estar en la misma sección.'
                })
            if instance:
                # Detección de ciclo: seguir cadena desde depende_de; si se llega a instance, hay ciclo
                campos_por_id = {c.pk: c for c in Campo.objects.filter(fecha_elimina__isnull=True).select_related('depende_de')}
                if _detectar_ciclo_dependencia(instance.pk, depende_de.pk, campos_por_id):
                    raise serializers.ValidationError({
                        'depende_de_id': 'No se permiten dependencias circulares.'
                    })

        visible_si = attrs.get('visible_si')
        OPERADORES = ('igual', 'diferente', 'contiene', 'mayor', 'menor')
        if visible_si is not None and visible_si != '' and visible_si != {}:
            if not isinstance(visible_si, dict):
                raise serializers.ValidationError({
                    'visible_si': 'Debe ser un objeto con "campo_id", "operador" y "valor", o null para sin condición.'
                })
            campo_id = visible_si.get('campo_id')
            valor = visible_si.get('valor')
            if campo_id is None and visible_si.get('campo') is not None:
                raise serializers.ValidationError({
                    'visible_si': 'Use "campo_id" (ID del campo), no "campo" (nombre).'
                })
            if not campo_id or not str(valor or '').strip():
                attrs['visible_si'] = None
            else:
                try:
                    cid = int(campo_id)
                except (TypeError, ValueError):
                    raise serializers.ValidationError({
                        'visible_si': '"campo_id" debe ser un número entero.'
                    })
                operador = (visible_si.get('operador') or 'igual').strip().lower()
                if operador not in OPERADORES:
                    operador = 'igual'
                attrs['visible_si'] = {
                    'campo_id': cid,
                    'operador': operador,
                    'valor': str(valor or '').strip(),
                }
        elif visible_si == '' or visible_si == {}:
            attrs['visible_si'] = None

        return attrs


class FormularioCampoSerializer(serializers.ModelSerializer):
    """Respuesta ligera para GET /api/formulario/?servicio_id=&contratista_id="""
    opciones = serializers.SerializerMethodField()
    depende_de_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Campo
        fields = [
            'id',
            'nombre',
            'tipo',
            'entidad',
            'depende_de',
            'depende_de_nombre',
            'placeholder',
            'seccion',
            'requerido',
            'visible_si',
            'opciones',
        ]

    def get_depende_de_nombre(self, obj):
        return obj.depende_de.nombre if obj.depende_de else None

    def get_opciones(self, obj):
        if obj.tipo == 'entity_select':
            return []
        if obj.tipo != 'select':
            return []
        opciones_activas = sorted(
            (o for o in obj.opciones.all() if o.activo and o.estado == '1'),
            key=lambda o: (o.orden, o.id),
        )
        return [{'label': o.label, 'value': o.value} for o in opciones_activas]
