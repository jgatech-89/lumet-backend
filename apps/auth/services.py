import uuid

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q

from config.utils import generate_verification_code
from config.email_service import send_otp_email

User = get_user_model()
CODE_TIMEOUT = getattr(settings, 'LOGIN_CODE_TIMEOUT', 600)
PWD_RESET_TOKEN_TIMEOUT = getattr(settings, 'PWD_RESET_TOKEN_TIMEOUT', 300)  # 5 min para cambiar contraseña

def _cache_key(correo):
    return f"auth_code:{str(correo).strip().lower()}"


def _pwd_reset_code_key(correo):
    return f"auth_pwd_reset_code:{str(correo).strip().lower()}"


def _pwd_reset_token_key(token):
    return f"auth_pwd_reset_token:{token}"

def find_user_by_correo(correo):
    """Busca usuario por correo (correo o email). Incluye correo_auth para envío de OTP."""
    c = str(correo).strip().lower()
    return User.objects.filter(Q(correo__iexact=c) | Q(email__iexact=c), estado='1').only(
        'id', 'correo', 'email', 'correo_auth', 'password', 'codigo_verificado', 'estado'
    ).first()

def validate_credentials(correo, password):
    """
    Valida correo y contraseña. Devuelve la Persona si son correctos y estado activo, sino None.
    No revela si el correo existe.
    """
    user = find_user_by_correo(correo)
    if not user or not user.check_password(password):
        return None
    if getattr(user, 'estado', None) != '1':
        return None
    return user

def create_and_send_code(user):
    """
    Genera código, lo guarda en user.codigo_verificado y en cache, envía email al correo auth.
    Devuelve True si todo ok.
    """
    code = generate_verification_code(6)
    user.codigo_verificado = code
    user.save(update_fields=['codigo_verificado'])
    email_key = (user.correo or user.email or '').strip().lower()
    cache.set(_cache_key(email_key), user.id, timeout=CODE_TIMEOUT)

    # Los códigos OTP se envían al correo auth (responsable/administrador), no al correo del usuario.
    recipient = getattr(user, 'correo_auth', None) or user.correo or user.email
    if not recipient:
        return False
    ok = send_otp_email(
        to=[recipient],
        code=code,
        subject='Código de confirmación - Lumet',
        message_title='Código de verificación',
        message_body='Utiliza el siguiente código para completar tu inicio de sesión en Lumet.',
        expiry_minutes=CODE_TIMEOUT // 60,
    )
    return ok

def validate_and_clear_code(correo, codigo):
    """
    Valida el código para el correo. Si es correcto limpia codigo_verificado y cache.
    Devuelve la Persona o None.
    """
    user = find_user_by_correo(correo)
    if not user:
        return None
    if not cache.get(_cache_key(correo)):
        return None
    if (user.codigo_verificado or '').strip() != str(codigo).strip():
        return None
    user.codigo_verificado = ''
    user.save(update_fields=['codigo_verificado'])
    cache.delete(_cache_key(correo))
    return user

def resend_code_for_correo(correo):
    """
    Si existe usuario con ese correo y está activo, genera nuevo código y envía email.
    Devuelve True si se envió, False si no (sin revelar motivo).
    """
    user = find_user_by_correo(correo)
    if not user or getattr(user, 'estado', None) != '1':
        return False
    return create_and_send_code(user)


def create_and_send_password_reset_code(user):
    """
    Genera código de recuperación, lo guarda en cache (no en user para no interferir con login),
    envía email. Devuelve True si todo ok.
    """
    code = generate_verification_code(6)
    email_key = (user.correo or user.email or '').strip().lower()
    cache.set(
        _pwd_reset_code_key(email_key),
        {'code': code, 'user_id': user.id},
        timeout=CODE_TIMEOUT,
    )
    recipient = getattr(user, 'correo_auth', None) or user.correo or user.email
    if not recipient:
        return False
    ok = send_otp_email(
        to=[recipient],
        code=code,
        subject='Recuperación de contraseña - Lumet',
        message_title='Código para recuperar tu contraseña',
        message_body='Solicitaste recuperar tu contraseña. Utiliza el siguiente código para continuar y definir una nueva contraseña.',
        expiry_minutes=CODE_TIMEOUT // 60,
    )
    return ok


def request_password_reset(correo):
    """
    Si existe usuario con ese correo y está activo, genera código y envía email de recuperación.
    Devuelve True si se envió, False si no (respuesta genérica al cliente).
    """
    user = find_user_by_correo(correo)
    if not user or getattr(user, 'estado', None) != '1':
        return False
    return create_and_send_password_reset_code(user)


def verify_password_reset_code(correo, codigo):
    """
    Valida el código de recuperación. Si es correcto, invalida el código y devuelve un token
    de un solo uso para el paso de cambiar contraseña. Devuelve el token (str) o None.
    """
    email_key = str(correo).strip().lower()
    key = _pwd_reset_code_key(email_key)
    data = cache.get(key)
    if not data or (data.get('code') or '').strip() != str(codigo).strip():
        return None
    user_id = data.get('user_id')
    if not user_id:
        return None
    token = str(uuid.uuid4())
    cache.delete(key)
    cache.set(_pwd_reset_token_key(token), user_id, timeout=PWD_RESET_TOKEN_TIMEOUT)
    return token


def reset_password_with_token(token, new_password):
    """
    Valida el token de recuperación, actualiza la contraseña del usuario y borra el token.
    Devuelve True si todo ok, False si token inválido o expirado.
    """
    key = _pwd_reset_token_key(token)
    user_id = cache.get(key)
    if not user_id:
        return False
    user = User.objects.filter(id=user_id).first()
    if not user:
        cache.delete(key)
        return False
    user.set_password(new_password)
    user.save(update_fields=['password'])
    cache.delete(key)
    return True
