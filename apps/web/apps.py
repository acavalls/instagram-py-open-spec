from django.apps import AppConfig


class WebConfig(AppConfig):
    """Configuration for the web app (HTMX UI layer)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.web"
