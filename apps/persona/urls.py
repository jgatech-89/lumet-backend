from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PersonaViewSet, VendedorViewSet

router = DefaultRouter()
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'vendedores', VendedorViewSet, basename='vendedor')

urlpatterns = [
    path('', include(router.urls)),
]
