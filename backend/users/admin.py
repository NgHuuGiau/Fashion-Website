from django.contrib import admin

from .models import UserActivity, UserProfile, VisitorSession
from .models_referral import ReferralCode, ReferralReward


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "user",
        "is_active",
        "usage_count",
        "max_usage",
        "created_at",
        "expires_at",
    )
    search_fields = ("code", "user__username")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("code", "created_at")


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = (
        "referral_code",
        "referrer",
        "referred_user",
        "reward_type",
        "amount",
        "is_claimed",
        "created_at",
    )
    search_fields = (
        "referral_code__code",
        "referrer__username",
        "referred_user__username",
    )
    list_filter = ("reward_type", "is_claimed", "created_at")
    readonly_fields = ("created_at",)


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_key",
        "user",
        "is_authenticated",
        "ip_address",
        "first_seen",
        "last_seen",
    )
    search_fields = ("session_key", "user__username", "ip_address")
    list_filter = ("is_authenticated", "first_seen", "last_seen")


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("event_type", "user", "path", "method", "status_code", "created_at")
    list_filter = ("event_type", "method", "status_code", "created_at")
    search_fields = ("user__username", "path")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number")
    search_fields = ("user__username", "phone_number")
