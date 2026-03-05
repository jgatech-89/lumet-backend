from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Persona
from .serializers import PersonaSerializer


@extend_schema_view(
    list=extend_schema(tags=['Personas'], summary='Listar personas'),
    create=extend_schema(tags=['Personas'], summary='Crear persona'),
    retrieve=extend_schema(tags=['Personas'], summary='Obtener persona'),
    update=extend_schema(tags=['Personas'], summary='Actualizar persona (PUT)'),
    partial_update=extend_schema(tags=['Personas'], summary='Actualizar persona (PATCH)'),
    destroy=extend_schema(tags=['Personas'], summary='Eliminar persona'),
)
class PersonaViewSet(viewsets.ModelViewSet):
    """CRUD de Personas. Requiere JWT (Authorization: Bearer <access_token>)."""
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    permission_classes = [IsAuthenticated]
