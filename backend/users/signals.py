from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models_referral import ReferralCode
from users.role_sync import write_role_to_legacy


@receiver(post_save, sender=User)
def sync_user_role_to_legacy(sender, instance, **kwargs):
    write_role_to_legacy(instance)


@receiver(post_save, sender=User)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        ReferralCode.objects.get_or_create(user=instance)
