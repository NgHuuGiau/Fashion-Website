from django.db import migrations


def set_default_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        id=1,
        defaults={"domain": "localhost:8000", "name": "HUUGIAU Atelier"},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(set_default_site, migrations.RunPython.noop),
    ]
