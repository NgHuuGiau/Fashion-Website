"""
Newsletter/Email Marketing services for Fashion-Website
Part 3: Campaign sending (background task)
"""
import logging
import smtplib
from email.message import EmailMessage

from django.conf import settings
from django.utils import timezone

from .models import EmailCampaign, NewsletterSubscriber

logger = logging.getLogger("fashion.newsletter")


def send_campaign_email(campaign_id: int) -> None:
    """Send campaign to all subscribers (background task)"""
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
    except EmailCampaign.DoesNotExist:
        logger.error("Campaign %s not found", campaign_id)
        return

    if not all((getattr(settings, "EMAIL_HOST", None), getattr(settings, "DEFAULT_FROM_EMAIL", None))):
        logger.warning("SMTP not configured for campaign %s", campaign_id)
        campaign.status = "failed"
        campaign.save(update_fields=["status"])
        return

    recipients = list(
        NewsletterSubscriber.objects.filter(is_active=True).values_list("email", flat=True)
    )
    if not recipients:
        logger.warning("No active subscribers for campaign %s", campaign_id)
        campaign.status = "failed"
        campaign.save(update_fields=["status"])
        return

    campaign.status = "sending"
    campaign.recipient_count = len(recipients)
    campaign.save(update_fields=["status", "recipient_count"])

    sent_count = 0
    failed_count = 0
    smtp_host = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_user = settings.EMAIL_HOST_USER
    smtp_pass = settings.EMAIL_HOST_PASSWORD
    mail_from = settings.DEFAULT_FROM_EMAIL
    use_tls = getattr(settings, "EMAIL_USE_TLS", True)

    try:
        from .services import render_campaign_email  # avoid circular import
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            if use_tls and hasattr(smtp, "has_extn") and smtp.has_extn("starttls"):
                try:
                    smtp.starttls()
                except Exception:
                    pass
            if smtp_user and smtp_pass:
                smtp.login(smtp_user, smtp_pass)

            for email in recipients:
                try:
                    text_content, html_content = render_campaign_email(
                        email, campaign.subject, campaign.body
                    )
                    message = EmailMessage()
                    message["From"] = mail_from
                    message["To"] = email
                    message["Subject"] = campaign.subject.strip()
                    message.set_content(text_content)
                    if html_content:
                        message.add_alternative(html_content, subtype="html")
                    smtp.send_message(message)
                    sent_count += 1
                except Exception as sub_exc:
                    logger.error("Error sending campaign to %s: %s", email, sub_exc)
                    failed_count += 1

        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.status = "sent" if failed_count == 0 else "failed"
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=["sent_count", "failed_count", "status", "sent_at"])

    except Exception as exc:
        logger.error("Fatal error during campaign %s dispatch: %s", campaign_id, exc)
        campaign.status = "failed"
        campaign.save(update_fields=["status"])