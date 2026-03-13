from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CampoViewSet,
    CampoOpcionViewSet,
    FormularioCamposAPIView,
    OpcionesEstadoVentaAPIView,
    OpcionesCampoPorNombreAPIView,
)

router = DefaultRouter()
router.register(r'campos', CampoViewSet, basename='campo')
router.register(r'campo-opciones', CampoOpcionViewSet, basename='campo-opcion')

urlpatterns = [
    path('campos/opciones-estado-venta/', OpcionesEstadoVentaAPIView.as_view(), name='opciones-estado-venta'),
    path('campos/opciones-por-nombre/', OpcionesCampoPorNombreAPIView.as_view(), name='opciones-por-nombre'),
    path('', include(router.urls)),
    path('formulario/', FormularioCamposAPIView.as_view(), name='formulario-campos'),
]
