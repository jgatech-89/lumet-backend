from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from . import services
from .schema.auth_schema import login_schema, me_schema, refresh_schema, resend_code_schema, verify_code_schema
from .serializers import LoginSerializer, ResendCodeSerializer, VerificarCodigoSerializer

MSG_CODE_SENT = 'Si las credenciales son correctas, recibirás un código en tu correo.'
MSG_CODE_RESENT = 'Si el correo está registrado, recibirás un nuevo código.'


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
        if user:
            services.create_and_send_code(user)
        return Response({'mensaje': MSG_CODE_SENT}, status=status.HTTP_200_OK)


@verify_code_schema
class VerificarCodigoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = VerificarCodigoSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        correo = ser.validated_data['correo'].strip().lower()
        codigo = ser.validated_data['codigo'].strip()
        user = services.validate_and_clear_code(correo, codigo)
        if not user:
            return Response({'detail': 'Código inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)
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
        services.resend_code_for_correo(correo)
        return Response({'mensaje': MSG_CODE_RESENT}, status=status.HTTP_200_OK)
