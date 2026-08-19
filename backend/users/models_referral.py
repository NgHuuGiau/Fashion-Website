import string
import random
from django.db import models
from django.conf import settings
from django.utils import timezone


class ReferralCode(models.Model):
    """Mã giới thiệu - tặng 50K cho người giới thiệu và 50K cho người được giới thiệu"""
    code = models.CharField(max_length=12, unique=True, db_index=True, verbose_name="Mã code")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="referral_codes",
        on_delete=models.CASCADE,
        verbose_name="Người sở hữu"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    max_usage = models.PositiveIntegerField(default=50, verbose_name="Số lần dùng tối đa")

    class Meta:
        verbose_name = "Mã giới thiệu"
        verbose_name_plural = "Mã giới thiệu"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        """Tạo mã 8 ký tự: REF + 5 random"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = "REF" + "".join(random.choices(chars, k=5))
            if not ReferralCode.objects.filter(code=code).exists():
                return code

    def can_use(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.usage_count >= self.max_usage:
            return False
        return True

    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=["usage_count"])


class ReferralReward(models.Model):
    """Ghi nhận phần thưởng referral"""
    REWARD_TYPE_CHOICES = [
        ("referrer", "Người giới thiệu"),
        ("referred", "Người được giới thiệu"),
    ]

    referral_code = models.ForeignKey(
        ReferralCode,
        related_name="rewards",
        on_delete=models.CASCADE,
        verbose_name="Mã giới thiệu"
    )
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="referral_rewards_given",
        on_delete=models.CASCADE,
        verbose_name="Người giới thiệu"
    )
    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="referral_rewards_received",
        on_delete=models.CASCADE,
        verbose_name="Người được giới thiệu"
    )
    reward_type = models.CharField(max_length=10, choices=REWARD_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=0, default=50000, verbose_name="Số tiền (đ)")
    order = models.ForeignKey(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referral_rewards",
        verbose_name="Đơn hàng liên quan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Phần thưởng giới thiệu"
        verbose_name_plural = "Phần thưởng giới thiệu"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_reward_type_display()} - {self.amount:,.0f}đ - {self.referred_user.username}"