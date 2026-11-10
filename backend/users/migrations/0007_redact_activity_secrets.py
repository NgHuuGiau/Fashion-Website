import re

from django.db import migrations


RESET_PATH = re.compile(r"(/quen-mat-khau/dat-lai/)[^/]+/[^/]+/?$", re.IGNORECASE)
SENSITIVE_KEYS = {
    "query",
    "email",
    "phone",
    "phone_number",
    "token",
    "code",
    "secret",
}


def redact_activity_secrets(apps, schema_editor):
    activity_model = apps.get_model("users", "UserActivity")
    database = schema_editor.connection.alias
    pending = []

    for activity in (
        activity_model.objects.using(database).all().iterator(chunk_size=500)
    ):
        path = RESET_PATH.sub(r"\1[redacted]/", activity.path or "")
        metadata = activity.metadata if isinstance(activity.metadata, dict) else {}
        metadata = dict(metadata)
        for key in list(metadata):
            if key.casefold() in SENSITIVE_KEYS:
                metadata.pop(key, None)

        if path != activity.path or metadata != activity.metadata:
            activity.path = path
            activity.metadata = metadata
            pending.append(activity)

        if len(pending) >= 500:
            activity_model.objects.using(database).bulk_update(
                pending, ["path", "metadata"]
            )
            pending.clear()

    if pending:
        activity_model.objects.using(database).bulk_update(
            pending, ["path", "metadata"]
        )


class Migration(migrations.Migration):
    dependencies = [("users", "0006_referral_program")]

    operations = [
        migrations.RunPython(redact_activity_secrets, migrations.RunPython.noop)
    ]
