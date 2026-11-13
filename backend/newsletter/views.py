"""
Newsletter views for Fashion-Website
Ported from ElectroHub - adapted for Fashion-Website
"""
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from .models import NewsletterSubscriber, EmailCampaign, EmailTemplate
from .services_send import send_welcome_email
from .services_campaign import send_campaign_email
from .models import verify_unsubscribe_token


@method_decorator(csrf_exempt, name="dispatch")
class SubscribeView(View):
    """POST /newsletter/subscribe/ - Subscribe email to newsletter"""

    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        if not email or "@" not in email:
            return JsonResponse({"success": False, "error": "Email không hợp lệ"}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={"source": "website"}
        )

        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=["is_active", "unsubscribed_at"])
            created = True

        if created:
            # Send welcome email async (use background task in production)
            try:
                send_welcome_email(email)
            except Exception:
                pass  # Don't fail subscription if email fails

        return JsonResponse({
            "success": True,
            "message": "Đăng ký nhận tin thành công! Kiểm tra email để nhận mã WELCOME10." if created else "Email đã đăng ký nhận tin."
        })


@method_decorator(csrf_exempt, name="dispatch")
class UnsubscribeView(View):
    """GET /newsletter/unsubscribe/?token=... - Unsubscribe via HMAC link"""

    def get(self, request):
        token = request.GET.get("token", "")
        email, valid = verify_unsubscribe_token(token)

        if not valid or not email:
            return JsonResponse({"success": False, "error": "Liên kết hủy đăng ký không hợp lệ"}, status=400)

        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save(update_fields=["is_active", "unsubscribed_at"])
            return JsonResponse({"success": True, "message": "Đã hủy đăng ký nhận tin thành công"})
        except NewsletterSubscriber.DoesNotExist:
            return JsonResponse({"success": True, "message": "Email không tồn tại trong danh sách"})


@method_decorator(staff_member_required, name="dispatch")
class AdminCampaignView(View):
    """Admin newsletter campaign management"""

    def get(self, request):
        """List campaigns and templates"""
        campaigns = EmailCampaign.objects.all()[:50]
        templates = EmailTemplate.objects.filter(is_active=True)

        return JsonResponse({
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "subject": c.subject,
                    "status": c.status,
                    "recipient_count": c.recipient_count,
                    "sent_count": c.sent_count,
                    "created_at": c.created_at.isoformat(),
                } for c in campaigns
            ],
            "templates": [
                {
                    "id": t.template_id,
                    "name": t.name,
                    "subject": t.subject,
                } for t in templates
            ]
        })

    def post(self, request):
        """Create and send campaign"""
        action = request.POST.get("action")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        template_id = request.POST.get("template_id", "").strip()

        if action == "preview":
            # Return preview HTML
            from .services import render_campaign_email
            text, html = render_campaign_email("preview@test.com", subject, body)
            return JsonResponse({"success": True, "preview_html": html})

        if not subject or not body:
            return JsonResponse({"success": False, "error": "Thiếu chủ đề hoặc nội dung"}, status=400)

        campaign = EmailCampaign.objects.create(
            name=f"Campaign {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            subject=subject,
            body=body,
            template_id=template_id,
            created_by=request.user if request.user.is_authenticated else None,
        )

        # Send async (in production use Celery)
        try:
            send_campaign_email(campaign.id)
        except Exception as exc:
            campaign.status = "failed"
            campaign.save(update_fields=["status"])
            return JsonResponse({"success": False, "error": str(exc)}, status=500)

        return JsonResponse({"success": True, "campaign_id": campaign.id, "message": "Đang gửi chiến dịch..."})


@method_decorator(staff_member_required, name="dispatch")
class AdminSubscriberView(View):
    """Admin subscriber management"""

    def get(self, request):
        subscribers = NewsletterSubscriber.objects.all()[:100]
        return JsonResponse({
            "subscribers": [
                {
                    "id": s.id,
                    "email": s.email,
                    "is_active": s.is_active,
                    "subscribed_at": s.subscribed_at.isoformat(),
                    "source": s.source,
                } for s in subscribers
            ],
            "total": NewsletterSubscriber.objects.count(),
            "active": NewsletterSubscriber.objects.filter(is_active=True).count(),
        })