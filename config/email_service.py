"""
Servicio centralizado de envío de correos.

Utiliza Resend cuando `RESEND_API_KEY` está configurada (producción).
Si no hay `RESEND_API_KEY`, no se envía el correo (para evitar configuraciones legacy/SMTP no deseadas).

"""
import logging

from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


_RESEND_SANDBOX_FALLBACK_FROM = "Lumet <onboarding@resend.dev>"


def _resend_from_address(from_email: str) -> str:
    """
    Resend puede rechazar dominios no verificados (p. ej. `.local`, `localhost`, etc.).
    Para mantener compatibilidad, en esos casos usamos un remitente de prueba fijo.
    """

    if not from_email:
        return _RESEND_SANDBOX_FALLBACK_FROM

    configured = str(from_email).strip()

    # Extraemos el email real si viene como "Nombre <email@dominio.com>"
    email = configured
    if "<" in configured and ">" in configured:
        email = configured.split("<")[-1].split(">")[0].strip()

    email_lower = email.lower()
    if ".local" in email_lower or "localhost" in email_lower or email_lower.endswith(".test"):
        return _RESEND_SANDBOX_FALLBACK_FROM

    # Si ya trae formato "Nombre <email>" lo respetamos.
    if "<" in configured and ">" in configured:
        return configured

    # Si llega como email plano, agregamos nombre.
    return f"Lumet <{configured}>"


def _render_otp_html(context):
    """Genera el HTML del correo OTP a partir del template."""
    return render_to_string('email/otp.html', context)


def send_otp_email(
    *,
    to,
    code,
    subject,
    message_title='Código de verificación',
    message_body=None,
    expiry_minutes=10,
):
    if isinstance(to, str):
        to = [to]
    to = [t.strip() for t in to if t and str(t).strip()]

    if not to:
        logger.warning('send_otp_email: no recipients')
        return False

    from_email = settings.RESEND_FROM_EMAIL
    logo_url = getattr(settings, 'LUMET_LOGO_URL', None)

    context = {
        'message_title': message_title,
        'message_body': message_body or 'Estás recibiendo este correo porque solicitaste un código de verificación. Utiliza el siguiente código para continuar:',
        'code': str(code).strip(),
        'expiry_minutes': expiry_minutes,
        'logo_url': logo_url,
    }

    api_key = getattr(settings, 'RESEND_API_KEY', None)

    if not api_key:
        logger.error('send_otp_email: RESEND_API_KEY no configurada')
        return False

    try:
        import resend

        resend.api_key = api_key
        html = _render_otp_html(context)
        params = {
            'from': _resend_from_address(from_email),
            'to': to,
            'subject': subject,
            'html': html,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.exception('send_otp_email (Resend) failed: %s', e)
        return False


def send_email(to, subject, html_content, text_content=None, from_email=None):

    if isinstance(to, str):
        to = [to]
    to = [t.strip() for t in to if t and str(t).strip()]
    if not to:
        logger.warning('send_email: no recipients')
        return False

    from_email = from_email or settings.RESEND_FROM_EMAIL
    api_key = getattr(settings, 'RESEND_API_KEY', None)

    if not api_key:
        logger.error('send_email: RESEND_API_KEY no configurada')
        return False

    try:
        import resend

        resend.api_key = api_key
        params = {
            'from': _resend_from_address(from_email),
            'to': to,
            'subject': subject,
            'html': html_content,
        }
        if text_content:
            params['text'] = text_content
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.exception('send_email (Resend) failed: %s', e)
        return False
