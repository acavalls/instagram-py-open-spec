import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """Post entity representing a user's Instagram post."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    owner = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    caption = models.TextField(blank=True, default="")  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)  # type: ignore
    updated_at = models.DateTimeField(auto_now=True)  # type: ignore

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Post {self.id} by {self.owner.username}"

    def can_edit(self, user_id: "uuid.UUID") -> tuple[bool, str]:
        """Check if a user can edit this post."""
        if self.owner_id != user_id:  # type: ignore[attr-defined]
            return False, "You can only edit your own posts"
        return True, ""

    def can_delete(self, user_id: "uuid.UUID") -> tuple[bool, str]:
        """Check if a user can delete this post."""
        if self.owner_id != user_id:  # type: ignore[attr-defined]
            return False, "You can only delete your own posts"
        return True, ""


class PostMedia(models.Model):
    """Media files (images/videos) attached to a post."""

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    post = models.ForeignKey(  # type: ignore
        Post,
        on_delete=models.CASCADE,
        related_name="media",
    )
    file = models.ImageField(upload_to="post_examples/%Y/%m/%d/")  # type: ignore
    media_type = models.CharField(  # type: ignore
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    order = models.PositiveIntegerField(default=0)  # type: ignore

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["post", "order"]),
        ]

    def __str__(self) -> str:
        return f"Media {self.id} for Post {self.post_id}"  # type: ignore


class Story(models.Model):
    """Story entity representing a temporary user story (expires after 24h)."""

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    owner = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stories",
    )
    file = models.ImageField(upload_to="stories/%Y/%m/%d/")  # type: ignore
    media_type = models.CharField(  # type: ignore
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # type: ignore
    expires_at = models.DateTimeField()  # type: ignore

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"Story {self.id} by {self.owner.username}"  # type: ignore

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at


class StoryView(models.Model):
    """Tracks which users have viewed a story."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # type: ignore
    story = models.ForeignKey(  # type: ignore
        Story,
        on_delete=models.CASCADE,
        related_name="views",
    )
    viewer = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="story_views",
    )
    viewed_at = models.DateTimeField(auto_now_add=True)  # type: ignore

    class Meta:
        ordering = ["-viewed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["story", "viewer"],
                name="unique_story_viewer",
            ),
        ]
        indexes = [
            models.Index(fields=["story", "viewer"]),
        ]

    def __str__(self) -> str:
        return f"StoryView {self.id}: {self.viewer.username} viewed {self.story_id}"  # type: ignore
