"""
URLs de la app relaciones.
Endpoints: /api/relaciones/ y /api/relaciones/opciones/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelacionViewSet

router = DefaultRouter()
router.register(r'relaciones', RelacionViewSet, basename='relacion')

urlpatterns = [
    path('', include(router.urls)),
]
