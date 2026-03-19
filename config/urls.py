"""
URL configuration for lumet_backend project.
Solo incluye las URLs de cada app; las rutas se definen en cada app.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path(settings.ADMIN_URL.lstrip("/"), admin.site.urls),
    path('auth/', include('apps.auth.urls')),
    path('api/', include('apps.core.urls')),
    path('api/', include('apps.persona.urls')),
    path('api/', include('apps.empresa.urls')),
    path('api/', include('apps.servicio.urls')),
    path('api/', include('apps.formularios.urls')),
    path('api/', include('apps.cliente.urls')),
    # Documentación OpenAPI (drf-spectacular)
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
