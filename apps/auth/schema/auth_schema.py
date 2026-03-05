"""
Documentación OpenAPI (drf-spectacular) para los endpoints de auth.
Decoradores reutilizables; sin lógica de negocio.
"""
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

from ..serializers import LoginSerializer, ResendCodeSerializer, VerificarCodigoSerializer

MSG_CODE_SENT = 'Si las credenciales son correctas, recibirás un código en tu correo.'
MSG_CODE_RESENT = 'Si el correo está registrado, recibirás un nuevo código.'


login_schema = extend_schema(
    tags=['Autenticación'],
    summary='Login (solicitar código)',
    description='Envía correo y contraseña. Si son válidos, se genera un código de 6 dígitos, '
                'se guarda en el usuario y se envía por correo. No devuelve token; usar verificar-codigo después.',
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description='Siempre 200 con mensaje genérico (no revela si el correo existe).',
            examples=[OpenApiExample('Éxito', value={'mensaje': MSG_CODE_SENT})],
        ),
        400: OpenApiResponse(description='Datos inválidos (formato correo/password).'),
    },
)


verify_code_schema = extend_schema(
    tags=['Autenticación'],
    summary='Verificar código y obtener JWT',
    description='Envía el correo y el código recibido por email. Si son correctos, '
                'se limpia el código y se devuelven access_token y refresh_token.',
    request=VerificarCodigoSerializer,
    responses={
        200: OpenApiResponse(
            description='Tokens JWT.',
            examples=[OpenApiExample(
                'Éxito',
                value={'access_token': 'eyJ...', 'refresh_token': 'eyJ...'},
            )],
        ),
        400: OpenApiResponse(description='Código inválido o expirado.'),
    },
)


refresh_schema = extend_schema(
    tags=['Autenticación'],
    summary='Refrescar access token',
    description='Intercambia un refresh_token válido por un nuevo access_token. Body: {"refresh": "<refresh_token>"}.',
    responses={
        200: OpenApiResponse(
            description='Nuevo access token.',
            examples=[OpenApiExample('Éxito', value={'access': 'eyJ...'})],
        ),
        401: OpenApiResponse(description='Refresh token inválido o expirado.'),
    },
)


me_schema = extend_schema(
    tags=['Autenticación'],
    summary='Usuario actual (me)',
    description='Devuelve los datos del usuario autenticado (JWT). Requiere header Authorization: Bearer <access_token>.',
    responses={
        200: OpenApiResponse(
            description='Datos del usuario.',
            examples=[OpenApiExample(
                'Éxito',
                value={
                    'id': 1,
                    'correo': 'usuario@ejemplo.com',
                    'primer_nombre': 'Juan',
                    'primer_apellido': 'Pérez',
                    'perfil': 'usuario',
                    'estado': '1',
                },
            )],
        ),
        401: OpenApiResponse(description='No autenticado o token inválido.'),
    },
)


resend_code_schema = extend_schema(
    tags=['Autenticación'],
    summary='Reenviar código',
    description='Solicita un nuevo código de verificación para el correo. '
                'Siempre responde con el mismo mensaje (no revela si el correo existe).',
    request=ResendCodeSerializer,
    responses={
        200: OpenApiResponse(
            description='Mensaje genérico.',
            examples=[OpenApiExample('Éxito', value={'mensaje': MSG_CODE_RESENT})],
        ),
        400: OpenApiResponse(description='Formato de correo inválido.'),
    },
)
