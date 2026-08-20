from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "One-shot sync of legacy [Users].role into auth_user flags."

    def handle(self, *args, **options):
        tables = [t.lower() for t in connection.introspection.table_names()]
        if "users" not in tables:
            self.stdout.write(
                self.style.WARNING("Legacy [Users] table not found; nothing to do.")
            )
            return
        rows = self._fetch("SELECT id, role FROM [Users]")
        updated = 0
        for row in rows:
            role = row["role"]
            is_super = role == 0
            is_staff = role in (0, 1)
            updated += (
                User.objects.filter(
                    id=row["id"],
                )
                .exclude(
                    is_superuser=is_super,
                    is_staff=is_staff,
                )
                .update(is_superuser=is_super, is_staff=is_staff)
            )
        self.stdout.write(self.style.SUCCESS(f"Synced {updated} users."))

    def _fetch(self, sql):
        with connection.cursor() as cur:
            cur.execute(sql)
            cols = [col[0] for col in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
