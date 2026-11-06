"""Social models — Follow relationships between users."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Follow(models.Model):
    """Represents a follow relationship between two users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    follower = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)  # type: ignore

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["follower", "-created_at"]),
            models.Index(fields=["following", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="no_self_follow",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.follower.username} follows {self.following.username}"  # type: ignore

    def is_self_follow(self) -> bool:
        """Check if this is a self-follow (follower == following)."""
        return self.follower_id == self.following_id  # type: ignore[attr-defined]

    def clean(self):
        """Validate that a user cannot follow themselves."""
        super().clean()
        if self.is_self_follow():
            raise ValidationError("You cannot follow yourself")
