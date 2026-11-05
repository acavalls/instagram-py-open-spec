import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

if not os.environ.get("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
