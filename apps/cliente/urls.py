from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')

# Rutas explícitas para acciones custom (prioridad sobre el router)
urlpatterns = [
    path('clientes/descargar-plantilla/', ClienteViewSet.as_view({'get': 'descargar_plantilla'}), name='cliente-descargar-plantilla'),
    path('clientes/importar-excel/', ClienteViewSet.as_view({'post': 'importar_excel'}), name='cliente-importar-excel'),
    path('clientes/exportar-excel/', ClienteViewSet.as_view({'get': 'exportar_excel'}), name='cliente-exportar-excel'),
    path('', include(router.urls)),
]
