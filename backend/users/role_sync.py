from django.db import connection


def _table_exists(name):
    tables = [t.lower() for t in connection.introspection.table_names()]
    return name.lower() in tables


def role_from_user(user):
    if user.is_superuser:
        return 0
    if user.is_staff:
        return 1
    return 2


def write_role_to_legacy(user):
    if not _table_exists("Users"):
        return
    role = role_from_user(user)
    with connection.cursor() as cur:
        cur.execute("UPDATE [Users] SET role = %s WHERE id = %s", [role, user.id])
