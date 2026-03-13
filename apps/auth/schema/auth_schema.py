"""
Documentación OpenAPI (drf-spectacular) para los endpoints de auth.
Decoradores reutilizables; sin lógica de negocio.
"""
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

from ..serializers import LoginSerializer, ResendCodeSerializer, VerificarCodigoSerializer, ForgotPasswordRequestSerializer, ForgotPasswordVerifySerializer, ForgotPasswordSetSerializer

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
            description='Credenciales válidas: mensaje y correo_auth (destinatario real del OTP).',
            examples=[OpenApiExample(
                'Éxito',
                value={'mensaje': MSG_CODE_SENT, 'correo_auth': 'admin@empresa.com'},
            )],
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
    description='Solicita un nuevo código de verificación. Si el usuario existe, puede incluir correo_auth (destinatario del OTP).',
    request=ResendCodeSerializer,
    responses={
        200: OpenApiResponse(
            description='Mensaje y opcionalmente correo_auth.',
            examples=[OpenApiExample(
                'Éxito',
                value={'mensaje': MSG_CODE_RESENT, 'correo_auth': 'admin@empresa.com'},
            )],
        ),
        400: OpenApiResponse(description='Formato de correo inválido.'),
    },
)


MSG_PWD_RESET_SENT = 'Si el correo está registrado, recibirás un código para recuperar tu contraseña.'
MSG_PWD_RESET_DONE = 'Contraseña actualizada. Ya puedes iniciar sesión con tu nueva contraseña.'

forgot_password_request_schema = extend_schema(
    tags=['Autenticación'],
    summary='Solicitar recuperación de contraseña',
    description='Envía el correo. Si está registrado y activo, se genera un código y se envía al correo auth; '
                'puede incluir correo_auth en la respuesta.',
    request=ForgotPasswordRequestSerializer,
    responses={
        200: OpenApiResponse(
            description='Mensaje y opcionalmente correo_auth (destinatario del código).',
            examples=[OpenApiExample(
                'Éxito',
                value={'mensaje': MSG_PWD_RESET_SENT, 'correo_auth': 'admin@empresa.com'},
            )],
        ),
        400: OpenApiResponse(description='Formato de correo inválido.'),
    },
)

forgot_password_verify_schema = extend_schema(
    tags=['Autenticación'],
    summary='Verificar código de recuperación',
    description='Envía correo y código recibido. Si son correctos, se devuelve un token de un solo uso '
                'para el endpoint de cambiar contraseña (forgot-password/set).',
    request=ForgotPasswordVerifySerializer,
    responses={
        200: OpenApiResponse(
            description='Token para cambiar contraseña.',
            examples=[OpenApiExample('Éxito', value={'token': 'uuid-del-token'})],
        ),
        400: OpenApiResponse(description='Código inválido o expirado.'),
    },
)

forgot_password_set_schema = extend_schema(
    tags=['Autenticación'],
    summary='Establecer nueva contraseña',
    description='Envía el token recibido tras verificar el código, la nueva contraseña y su confirmación. '
                'Si el token es válido, se actualiza la contraseña y el token se invalida.',
    request=ForgotPasswordSetSerializer,
    responses={
        200: OpenApiResponse(
            description='Contraseña actualizada.',
            examples=[OpenApiExample('Éxito', value={'mensaje': MSG_PWD_RESET_DONE})],
        ),
        400: OpenApiResponse(description='Token expirado/inválido o contraseñas no coinciden.'),
    },
)
