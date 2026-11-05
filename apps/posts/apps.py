from django.apps import AppConfig


class PostsConfig(AppConfig):
    """Configuration for the posts app (user content)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.posts"
