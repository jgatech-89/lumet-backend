from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Q

from config.utils import generate_verification_code

User = get_user_model()
CODE_TIMEOUT = getattr(settings, 'LOGIN_CODE_TIMEOUT', 600)

def _cache_key(correo):
    return f"auth_code:{str(correo).strip().lower()}"

def find_user_by_correo(correo):
    c = str(correo).strip().lower()
    return User.objects.filter(Q(correo__iexact=c) | Q(email__iexact=c), estado= '1').only('id', 'correo', 'email', 'password', 'codigo_verificado', 'estado').first()

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
    Genera código, lo guarda en user.codigo_verificado y en cache, envía email.
    Devuelve True si todo ok.
    """
    code = generate_verification_code(6)
    user.codigo_verificado = code
    user.save(update_fields=['codigo_verificado'])
    email_key = (user.correo or user.email or '').strip().lower()
    cache.set(_cache_key(email_key), user.id, timeout=CODE_TIMEOUT)

    send_mail(
        subject='Código de confirmación - Lumet',
        message=f'Tu código de confirmación es: {code}\n\nVálido por {CODE_TIMEOUT // 60} minutos.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.correo or user.email],
        fail_silently=False,
    )
    return True

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
