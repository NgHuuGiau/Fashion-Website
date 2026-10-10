"""Authenticated staff test client for business tests outside the 2FA flow."""

from django.contrib.auth import get_user_model
from django.test import Client
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from .permissions import is_staff_member


class VerifiedStaffClient(Client):
    def login(self, **credentials):
        result = super().login(**credentials)
        if result:
            user = get_user_model().objects.get(pk=self.session["_auth_user_id"])
            self._verify_staff(user)
        return result

    def force_login(self, user, backend=None):
        super().force_login(user, backend=backend)
        self._verify_staff(user)

    def _verify_staff(self, user):
        if is_staff_member(user):
            device, _ = TOTPDevice.objects.get_or_create(
                user=user, name="test", defaults={"confirmed": True}
            )
            session = self.session
            session[DEVICE_ID_SESSION_KEY] = device.persistent_id
            session.save()
