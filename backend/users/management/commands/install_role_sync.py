from django.core.management.base import BaseCommand
from django.db import connection

TRIGGER_NAME = "trg_Users_SyncAuthRole"

DROP_TRIGGER_SQL = """
IF OBJECT_ID(N'[dbo].[trg_Users_SyncAuthRole]', N'TR') IS NOT NULL
    DROP TRIGGER [dbo].[trg_Users_SyncAuthRole];
"""

CREATE_TRIGGER_SQL = """
CREATE TRIGGER [dbo].[trg_Users_SyncAuthRole] ON [dbo].[Users]
AFTER INSERT, UPDATE AS
BEGIN
    SET NOCOUNT ON;
    UPDATE au SET
        au.is_superuser = CASE WHEN ins.role = 0 THEN 1 ELSE 0 END,
        au.is_staff = CASE WHEN ins.role IN (0, 1) THEN 1 ELSE 0 END
    FROM dbo.auth_user AS au
    INNER JOIN inserted AS ins ON au.id = ins.id
    WHERE au.is_superuser <> CASE WHEN ins.role = 0 THEN 1 ELSE 0 END
       OR au.is_staff <> CASE WHEN ins.role IN (0, 1) THEN 1 ELSE 0 END;
END
"""


class Command(BaseCommand):
    help = "Install SQL Server trigger so [Users].role changes update auth_user flags."

    def handle(self, *args, **options):
        tables = [t.lower() for t in connection.introspection.table_names()]
        if "users" not in tables:
            self.stdout.write(
                self.style.WARNING("Legacy [Users] table not found; nothing to do.")
            )
            return
        with connection.cursor() as cur:
            cur.execute(DROP_TRIGGER_SQL)
            cur.execute(CREATE_TRIGGER_SQL)
        self.stdout.write(self.style.SUCCESS(f"Trigger {TRIGGER_NAME} installed."))
