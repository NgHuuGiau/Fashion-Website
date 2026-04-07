from django.conf import settings
from django.db import models



# ------------------------------------
# | KHỐI LỚP (CLASS): VISITORSESSION |
# ------------------------------------
class VisitorSession(models.Model):
    session_key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_authenticated = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):
        who = self.user.username if self.user else "guest"
        return f"{self.session_key} ({who})"



# ----------------------------------
# | KHỐI LỚP (CLASS): USERACTIVITY |
# ----------------------------------
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


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["path", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} {self.path} ({self.created_at:%Y-%m-%d %H:%M:%S})"



# ---------------------------------
# | KHỐI LỚP (CLASS): USERPROFILE |
# ---------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"{self.user.username} - {self.phone_number or 'No phone'}"
