from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpresaViewSet

# El Router genera automáticamente:
# GET /empresas/          -> Listar
# POST /empresas/         -> Crear
# GET /empresas/<id>/     -> Ver detalle
# PUT /empresas/<id>/     -> Actualizar
# DELETE /empresas/<id>/  -> Borrar lógico
router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')

urlpatterns = [
    path('', include(router.urls)),
]