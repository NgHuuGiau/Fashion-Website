from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsletter"
    verbose_name = "Newsletter & Email Marketing"

    def ready(self):
        # Import signals if any
        pass
