from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet

# GET /servicios/          -> Listar
# POST /servicios/        -> Crear
# GET /servicios/<id>/    -> Ver detalle
# PUT /servicios/<id>/    -> Actualizar
# DELETE /servicios/<id>/ -> Borrado lógico
router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicio')

urlpatterns = [
    path('', include(router.urls)),
]