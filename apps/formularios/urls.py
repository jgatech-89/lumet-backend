from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CampoViewSet, CampoOpcionViewSet, FormularioCamposAPIView

router = DefaultRouter()
router.register(r'campos', CampoViewSet, basename='campo')
router.register(r'campo-opciones', CampoOpcionViewSet, basename='campo-opcion')

urlpatterns = [
    path('', include(router.urls)),
    path('formulario/', FormularioCamposAPIView.as_view(), name='formulario-campos'),
]
