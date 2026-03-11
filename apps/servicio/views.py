from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Servicio
from .serializers import ServicioSerializer


class ServicioViewSet(viewsets.ModelViewSet):
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Servicio.objects.select_related(
            'empresa',
            'usuario_registra',
            'usuario_edita',
            'usuario_elimina',
        ).all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'mensaje': 'Servicio creado exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'mensaje': 'Servicio actualizado exitosamente.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(usuario_edita=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estado = '0'
        instance.estado_servicio = '0'
        instance.usuario_elimina = request.user
        instance.fecha_elimina = timezone.now()
        instance.save()
        return Response(
            {'mensaje': 'Servicio eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )
