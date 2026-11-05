import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with UUID primary key and unique email."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    email = models.EmailField(unique=True)  # type: ignore[var-annotated]
    bio = models.TextField(blank=True, default="")  # type: ignore
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # type: ignore

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return self.username

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if an email is already registered."""
        return User.objects.filter(email=email).exists()

    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if a username is already taken."""
        return User.objects.filter(username=username).exists()

    @classmethod
    def validate_registration(cls, email: str, username: str) -> tuple[bool, str]:
        """Validate registration data for duplicate email/username."""
        if cls.email_exists(email):
            return False, "Email already registered"
        if cls.username_exists(username):
            return False, "Username already taken"
        return True, ""
