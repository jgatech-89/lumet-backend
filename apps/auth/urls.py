from django.urls import path

from .views import LoginView, MeView, RefreshView, ResendCodeView, VerificarCodigoView

urlpatterns = [
    path('login', LoginView.as_view(), name='auth_login'),
    path('verificar-codigo', VerificarCodigoView.as_view(), name='auth_verificar_codigo'),
    path('refresh', RefreshView.as_view(), name='auth_refresh'),
    path('me', MeView.as_view(), name='auth_me'),
    path('resend-code', ResendCodeView.as_view(), name='auth_resend_code'),
]
