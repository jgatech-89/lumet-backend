from django.urls import path

from .views import (
    LoginView,
    MeView,
    RefreshView,
    ResendCodeView,
    VerificarCodigoView,
    ForgotPasswordRequestView,
    ForgotPasswordVerifyView,
    ForgotPasswordSetView,
)

urlpatterns = [
    path('login', LoginView.as_view(), name='auth_login'),
    path('verificar-codigo', VerificarCodigoView.as_view(), name='auth_verificar_codigo'),
    path('refresh', RefreshView.as_view(), name='auth_refresh'),
    path('me', MeView.as_view(), name='auth_me'),
    path('resend-code', ResendCodeView.as_view(), name='auth_resend_code'),
    # Recuperación de contraseña
    path('forgot-password/request', ForgotPasswordRequestView.as_view(), name='auth_forgot_password_request'),
    path('forgot-password/verify', ForgotPasswordVerifyView.as_view(), name='auth_forgot_password_verify'),
    path('forgot-password/set', ForgotPasswordSetView.as_view(), name='auth_forgot_password_set'),
]
