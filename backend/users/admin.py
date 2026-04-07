from django.contrib import admin

from .models import UserActivity, UserProfile, VisitorSession


@admin.register(VisitorSession)

# -----------------------------------------
# | KHỐI LỚP (CLASS): VISITORSESSIONADMIN |
# -----------------------------------------
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "user", "is_authenticated", "ip_address", "first_seen", "last_seen")
    search_fields = ("session_key", "user__username", "ip_address")
    list_filter = ("is_authenticated", "first_seen", "last_seen")


@admin.register(UserActivity)

# ---------------------------------------
# | KHỐI LỚP (CLASS): USERACTIVITYADMIN |
# ---------------------------------------
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("event_type", "user", "path", "method", "status_code", "created_at")
    list_filter = ("event_type", "method", "status_code", "created_at")
    search_fields = ("user__username", "path")


@admin.register(UserProfile)

# --------------------------------------
# | KHỐI LỚP (CLASS): USERPROFILEADMIN |
# --------------------------------------
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number")
    search_fields = ("user__username", "phone_number")
