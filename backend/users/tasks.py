"""Celery tasks for users app."""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def expire_points(self):
    """Hết hạn điểm thưởng hàng ngày (chạy lúc 3 AM)."""
    from users.models import UserProfile

    try:
        logger.info("Starting points expiry check...")

        # Tìm các profile có points_expire_at là hôm nay hoặc đã quá hạn
        expired_profiles = UserProfile.objects.filter(
            points_expire_at__lte=timezone.now(),
            points__gt=0,
        )

        expired_count = 0
        total_points_expired = 0

        for profile in expired_profiles:
            points_to_expire = profile.points
            profile.points = 0
            profile.points_expire_at = None
            profile.save(update_fields=["points", "points_expire_at"])
            expired_count += 1
            total_points_expired += points_to_expire

            logger.info(f"Expired {points_to_expire} points for user {profile.user_id}")

        if expired_count > 0:
            logger.info(
                f"Expired points for {expired_count} users, total {total_points_expired} points"
            )

        return {
            "expired_count": expired_count,
            "total_points_expired": total_points_expired,
        }
    except Exception as exc:
        logger.error(f"expire_points failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_welcome_email(self, user_id):
    """Gửi email chào mừng khi user đăng ký."""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject="Chào mừng bạn đến với HUUGIAU Atelier!",
            message=f"""Chào {user.first_name or user.username},

Chào mừng bạn đến với HUUGIAU Atelier! 

Tài khoản của bạn đã được tạo thành công. Bạn có thể:
- Mua hàng nhanh hơn với thông tin đã lưu
- Theo dõi đơn hàng thực thời
- Tích điểm thưởng mỗi đơn hàng
- Lưu wishlist sản phẩm yêu thích

Nếu có thắc mắc, hãy xem các kênh liên hệ hiện có trên website.

Trân trọng,
HUUGIAU Atelier Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to user {user_id}")
        return {"status": "sent", "user_id": user_id}
    except Exception as exc:
        logger.error(f"send_welcome_email failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_password_reset_email(self, user_id, reset_url):
    """Gửi email đặt lại mật khẩu."""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject="Đặt lại mật khẩu HUUGIAU Atelier",
            message=f"""Chào {user.first_name or user.username},

Bạn đã yêu cầu đặt lại mật khẩu. Nhấn vào link dưới đây để đặt lại (hết hạn sau 1 ngày):

{reset_url}

Nếu bạn không yêu cầu, hãy bỏ qua email này.

Trân trọng,
HUUGIAU Atelier Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to user {user_id}")
        return {"status": "sent", "user_id": user_id}
    except Exception as exc:
        logger.error(f"send_password_reset_email failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_order_confirmation_email(self, order_id):
    """Gửi email xác nhận đơn hàng."""
    from orders.models import Order
    from orders.services.order_email import send_order_email

    try:
        order = Order.objects.select_related("user").get(id=order_id)
        send_order_email(order.user, event="created", order=order)
        logger.info(f"Order confirmation email sent for order {order_id}")
        return {"status": "sent", "order_id": order_id}
    except Exception as exc:
        logger.error(
            f"send_order_confirmation_email failed for order {order_id}: {exc}"
        )
        raise self.retry(exc=exc)


@shared_task
def send_referral_reward_notification(self, user_id, reward_type, amount):
    """Gửi thông báo khi nhận được thưởng giới thiệu."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        reward_text = "điểm" if reward_type == "points" else f"{amount:,}đ"

        send_mail(
            subject=f"Bạn nhận được thưởng giới thiệu: {reward_text}",
            message=f"""Chào {user.first_name or user.username},

Bạn vừa nhận được thưởng giới thiệu: {reward_text}.

Cảm ơn bạn đã giới thiệu bạn bè đến với HUUGIAU Atelier!

Trân trọng,
HUUGIAU Atelier Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Referral reward notification sent to user {user_id}")
        return {"status": "sent", "user_id": user_id}
    except Exception as exc:
        logger.error(
            f"send_referral_reward_notification failed for user {user_id}: {exc}"
        )
        raise self.retry(exc=exc)
