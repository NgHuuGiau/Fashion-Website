"""
Newsletter/Email Marketing services for Fashion-Website
Part 2: SMTP sending functions
"""

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from django.conf import settings


logger = logging.getLogger("fashion.newsletter")


def send_smtp_message(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: Optional[str] = None,
) -> bool:
    """Send email via SMTP"""
    smtp_host = getattr(settings, "EMAIL_HOST", None)
    smtp_port = getattr(settings, "EMAIL_PORT", 587)
    smtp_user = getattr(settings, "EMAIL_HOST_USER", None)
    smtp_pass = getattr(settings, "EMAIL_HOST_PASSWORD", None)
    mail_from = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    use_tls = getattr(settings, "EMAIL_USE_TLS", True)

    if not all((smtp_host, mail_from)):
        logger.warning("SMTP not configured, skipping email send")
        return False

    try:
        message = EmailMessage()
        message["From"] = mail_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_content)
        if html_content:
            message.add_alternative(html_content, subtype="html")

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
            if use_tls and hasattr(smtp, "has_extn") and smtp.has_extn("starttls"):
                try:
                    smtp.starttls()
                except Exception:
                    pass
            if smtp_user and smtp_pass:
                smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


def send_welcome_email(email: str) -> bool:
    """Send welcome email with voucher (sync)"""
    try:
        from .services import render_welcome_email  # avoid circular import

        text_content, html_content = render_welcome_email(email)
        return send_smtp_message(
            to_email=email,
            subject="Chào mừng bạn đến với HUUGIAU Fashion! Tặng mã ưu đãi WELCOME10",
            text_content=text_content,
            html_content=html_content,
        )
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", email, exc)
        return False
