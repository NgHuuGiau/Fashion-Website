"""
Newsletter/Email Marketing services for Fashion-Website
Part 1: Core email functions
"""
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import generate_unsubscribe_token

logger = logging.getLogger("fashion.newsletter")


def get_unsubscribe_url(email: str) -> str:
    """Generate unsubscribe URL with HMAC token"""
    token = generate_unsubscribe_token(email)
    return f"{settings.SITE_URL}/newsletter/unsubscribe?{urlencode({'token': token})}"


def render_welcome_email(email: str) -> tuple[str, str]:
    """Render welcome email with voucher"""
    context = {
        "site_url": settings.SITE_URL,
        "unsubscribe_url": get_unsubscribe_url(email),
        "voucher_code": "WELCOME10",
        "subject": "Chào mừng bạn đến với HUUGIAU Fashion! Tặng mã ưu đãi WELCOME10",
    }
    html_content = render_to_string("emails/welcome.html", context)
    text_content = strip_tags(html_content)
    return text_content, html_content


def render_campaign_email(email: str, subject: str, body: str) -> tuple[str, str]:
    """Render marketing campaign email"""
    context = {
        "site_url": settings.SITE_URL,
        "unsubscribe_url": get_unsubscribe_url(email),
        "subject": subject,
        "body": body,
    }
    html_content = render_to_string("emails/campaign.html", context)
    text_content = strip_tags(html_content)
    return text_content, html_content