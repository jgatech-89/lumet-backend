from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from . import services
from .schema.auth_schema import (login_schema, me_schema, refresh_schema, resend_code_schema, verify_code_schema, forgot_password_request_schema, forgot_password_verify_schema, forgot_password_set_schema)
from .serializers import (LoginSerializer, ResendCodeSerializer, VerificarCodigoSerializer, ForgotPasswordRequestSerializer, ForgotPasswordVerifySerializer, ForgotPasswordSetSerializer)

MSG_CODE_SENT = 'Se ha enviado un código de verificación a tu correo.'
MSG_CODE_RESENT = 'Si el correo está registrado, recibirás un nuevo código.'
MSG_INVALID_CREDENTIALS = 'Correo o contraseña incorrectos.'
MSG_PWD_RESET_SENT = 'Si el correo está registrado, recibirás un código para recuperar tu contraseña.'
MSG_PWD_RESET_DONE = 'Contraseña actualizada. Ya puedes iniciar sesión con tu nueva contraseña.'


@login_schema
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        correo = ser.validated_data['correo'].strip().lower()
        password = ser.validated_data['password']
        user = services.validate_credentials(correo, password)
        if not user:
            return Response(
                {'detail': MSG_INVALID_CREDENTIALS},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        services.create_and_send_code(user)
        correo_auth = getattr(user, 'correo_auth', None) or user.correo or user.email or ''
        return Response({'mensaje': MSG_CODE_SENT, 'correo_auth': correo_auth}, status=status.HTTP_200_OK)


class VerificarCodigoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = VerificarCodigoSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        correo = ser.validated_data['correo'].strip().lower()
        codigo = ser.validated_data['codigo'].strip()

        result = services.validate_and_clear_code(correo, codigo)

        # 🔥 DEBUG RESPONSE
        if not result["ok"]:
            return Response({
                "detail": "DEBUG",
                "error": result["error"],
                "debug": result
            }, status=status.HTTP_400_BAD_REQUEST)

        user = result["user"]

        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_200_OK)


@refresh_schema
class RefreshView(TokenRefreshView):
    """Wrapper de TokenRefreshView para documentación en OpenAPI."""


@me_schema
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'correo': user.correo or user.email or '',
            'primer_nombre': user.primer_nombre or user.first_name or '',
            'primer_apellido': user.primer_apellido or user.last_name or '',
            'perfil': getattr(user, 'perfil', ''),
            'estado': getattr(user, 'estado', ''),
        }, status=status.HTTP_200_OK)


@resend_code_schema
class ResendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ResendCodeSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        correo = ser.validated_data['correo'].strip().lower()
        user = services.find_user_by_correo(correo)
        services.resend_code_for_correo(correo)
        payload = {'mensaje': MSG_CODE_RESENT}
        if user:
            correo_auth = getattr(user, 'correo_auth', None) or user.correo or user.email or ''
            if correo_auth:
                payload['correo_auth'] = correo_auth
        return Response(payload, status=status.HTTP_200_OK)


# ─── Recuperación de contraseña ───

@forgot_password_request_schema
class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ForgotPasswordRequestSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        correo = ser.validated_data['correo'].strip().lower()
        user = services.find_user_by_correo(correo)
        sent = services.request_password_reset(correo)
        payload = {'mensaje': MSG_PWD_RESET_SENT}
        if user and sent:
            correo_auth = getattr(user, 'correo_auth', None) or user.correo or user.email or ''
            if correo_auth:
                payload['correo_auth'] = correo_auth
        return Response(payload, status=status.HTTP_200_OK)


@forgot_password_verify_schema
class ForgotPasswordVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ForgotPasswordVerifySerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        correo = ser.validated_data['correo'].strip().lower()
        codigo = ser.validated_data['codigo'].strip()
        token = services.verify_password_reset_code(correo, codigo)
        if not token:
            return Response(
                {'detail': 'Código inválido o expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'token': token}, status=status.HTTP_200_OK)


@forgot_password_set_schema
class ForgotPasswordSetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ForgotPasswordSetSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        token = ser.validated_data['token']
        new_password = ser.validated_data['nueva_password']
        if not services.reset_password_with_token(token, new_password):
            return Response(
                {'detail': 'Enlace expirado o inválido. Solicita nuevamente la recuperación de contraseña.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'mensaje': MSG_PWD_RESET_DONE}, status=status.HTTP_200_OK)
