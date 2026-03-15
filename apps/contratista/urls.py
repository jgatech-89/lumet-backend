from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratistaViewSet

router = DefaultRouter()
router.register(r'contratistas', ContratistaViewSet, basename='contratista')

urlpatterns = [
    path('', include(router.urls)),
]
