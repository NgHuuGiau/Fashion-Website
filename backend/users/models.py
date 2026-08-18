from django.conf import settings
from django.db import models



class VisitorSession(models.Model):
    session_key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_authenticated = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):
        who = self.user.username if self.user else "guest"
        return f"{self.session_key} ({who})"



class UserActivity(models.Model):
    EVENT_CHOICES = [
        ("page_view", "Page View"),
        ("action", "Action"),
        ("register", "Register"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("cart_add", "Cart Add"),
        ("checkout", "Checkout"),
    ]

    visitor = models.ForeignKey(VisitorSession, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default="page_view")
    path = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=10, blank=True)
    status_code = models.PositiveIntegerField(default=200)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["path", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} {self.path} ({self.created_at:%Y-%m-%d %H:%M:%S})"



class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=40, blank=True, verbose_name="Nhãn (Nhà / Công ty)")
    recipient_name = models.CharField(max_length=150, verbose_name="Người nhận")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ")
    is_default = models.BooleanField(default=False, verbose_name="Mặc định", db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Địa chỉ giao hàng"
        verbose_name_plural = "Địa chỉ giao hàng"
        ordering = ["-is_default", "-created"]

    def __str__(self):
        return f"{self.recipient_name} - {self.address[:40]}"

    def save(self, *args, **kwargs):
        if self.is_default:
            self.__class__.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True)
    points = models.PositiveIntegerField(default=0, verbose_name="Điểm tích lũy", db_index=True)

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"{self.user.username} - {self.phone_number or 'No phone'}"

    def tier_name(self):
        if self.points >= 2000:
            return "VIP"
        if self.points >= 1000:
            return "Thân thiết"
        return "Thành viên"

    def tier(self):
        tiers = [
            {"threshold": 2000, "name": "VIP", "badge": "gold", "benefit": "Freeship mọi đơn · hỗ trợ ưu tiên · quà tặng sinh nhật"},
            {"threshold": 1000, "name": "Thân thiết", "badge": "silver", "benefit": "Freeship từ 299K · ưu đãi riêng hằng tháng"},
            {"threshold": 0, "name": "Thành viên", "badge": "bronze", "benefit": "Tích 1K = 1 điểm, đổi voucher mỗi đơn"},
        ]
        current = tiers[-1]
        for tier in tiers:
            if self.points >= tier["threshold"]:
                current = tier
                break
        nxt = None
        for tier in tiers:
            if tier["threshold"] > self.points:
                nxt = tier
                break
        progress = 0
        remaining = 0
        if nxt:
            prev = current["threshold"]
            span = nxt["threshold"] - prev
            progress = min(int((self.points - prev) / span * 100), 100) if span else 100
            remaining = nxt["threshold"] - self.points
        return {
            "name": current["name"],
            "badge": current["badge"],
            "benefit": current["benefit"],
            "points": self.points,
            "next": nxt,
            "progress": progress,
            "remaining": remaining,
        }
