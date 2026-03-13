"""
Servicio centralizado de envío de correos.

Utiliza Resend cuando RESEND_API_KEY está configurada (producción).
Si no, hace fallback al backend de email de Django (p. ej. consola en desarrollo).

Uso:
    from config.email_service import send_otp_email

    send_otp_email(
        to=['usuario@ejemplo.com'],
        code='123456',
        subject='Código de confirmación - Lumet',
        message_title='Código de verificación',
        message_body='Utiliza este código para completar tu inicio de sesión.',
        expiry_minutes=10,
    )
"""
import logging

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _resend_from_address(configured_from):
    """
    Si el remitente configurado usa un dominio no verificado (.local, localhost, etc.),
    Resend rechaza el envío. En ese caso usamos el remitente de prueba (RESEND_SANDBOX_FROM).
    """
    if not configured_from:
        return getattr(settings, 'RESEND_SANDBOX_FROM', 'Lumet <onboarding@resend.dev>')
    email = configured_from
    if '<' in configured_from and '>' in configured_from:
        email = configured_from.split('<')[-1].split('>')[0].strip()
    email_lower = email.lower()
    if '.local' in email_lower or 'localhost' in email_lower or email_lower.endswith('.test'):
        return getattr(settings, 'RESEND_SANDBOX_FROM', 'Lumet <onboarding@resend.dev>')
    if '<' in configured_from and '>' in configured_from:
        return configured_from
    return f'Lumet <{configured_from}>'


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
    """
    Envía un correo con código OTP usando el template de Lumet.

    Reutilizable para login, recuperación de contraseña y otros flujos OTP.

    Args:
        to: lista de correos destinatarios o un solo string.
        code: código de 6 dígitos (str).
        subject: asunto del correo.
        message_title: título dentro del correo (ej. "Código de verificación").
        message_body: texto principal; si es None se usa un texto por defecto.
        expiry_minutes: minutos de validez del código (se muestra en el correo).

    Returns:
        True si el envío fue exitoso, False en caso contrario.
    """
    if isinstance(to, str):
        to = [to]
    to = [t.strip() for t in to if t and str(t).strip()]

    if not to:
        logger.warning('send_otp_email: no recipients')
        return False

    from_email = getattr(settings, 'RESEND_FROM_EMAIL', None) or settings.DEFAULT_FROM_EMAIL
    logo_url = getattr(settings, 'LUMET_LOGO_URL', None)

    context = {
        'message_title': message_title,
        'message_body': message_body or 'Estás recibiendo este correo porque solicitaste un código de verificación. Utiliza el siguiente código para continuar:',
        'code': str(code).strip(),
        'expiry_minutes': expiry_minutes,
        'logo_url': logo_url,
    }

    api_key = getattr(settings, 'RESEND_API_KEY', None)

    if api_key:
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

    # Fallback: Django backend (consola, SMTP, etc.) con texto plano
    try:
        plain_body = f"{message_title}\n\n{context['message_body']}\n\nTu código: {code}\n\nVálido por {expiry_minutes} minutos."
        django_send_mail(
            subject=subject,
            message=plain_body,
            from_email=from_email,
            recipient_list=to,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.exception('send_otp_email (Django fallback) failed: %s', e)
        return False


def send_email(to, subject, html_content, text_content=None, from_email=None):
    """
    Envía un correo genérico (para futuros usos: invitaciones, notificaciones).

    Si RESEND_API_KEY está configurada usa Resend; si no, usa el backend de Django.

    Args:
        to: lista de correos o un solo string.
        subject: asunto.
        html_content: cuerpo en HTML.
        text_content: cuerpo en texto plano (opcional; en Resend puede generarse desde HTML).
        from_email: remitente (opcional; por defecto RESEND_FROM_EMAIL o DEFAULT_FROM_EMAIL).

    Returns:
        True si se envió correctamente, False en caso contrario.
    """
    if isinstance(to, str):
        to = [to]
    to = [t.strip() for t in to if t and str(t).strip()]
    if not to:
        logger.warning('send_email: no recipients')
        return False

    from_email = from_email or getattr(settings, 'RESEND_FROM_EMAIL', None) or settings.DEFAULT_FROM_EMAIL
    api_key = getattr(settings, 'RESEND_API_KEY', None)

    if api_key:
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

    try:
        django_send_mail(
            subject=subject,
            message=text_content or 'Contenido en formato HTML.',
            from_email=from_email,
            recipient_list=to,
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.exception('send_email (Django fallback) failed: %s', e)
        return False
