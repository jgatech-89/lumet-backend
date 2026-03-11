"""
URL configuration for lumet_backend project.
Solo incluye las URLs de cada app; las rutas se definen en cada app.
"""
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseForbidden
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('auth/', include('apps.auth.urls')),
    path('api/', include('apps.persona.urls')),
    path('api/', include('apps.empresa.urls')),
    path('api/', include('apps.servicio.urls')),
    # Documentación OpenAPI (drf-spectacular)
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Admin solo en desarrollo (no accesible en producción)
if settings.DEBUG:
    urlpatterns.insert(0, path('admin/', admin.site.urls))
else:

    def admin_forbidden(request):
        return HttpResponseForbidden('<h1>403</h1><p>Admin no disponible en producción.</p>')

    urlpatterns.insert(0, path('admin/', admin_forbidden))
