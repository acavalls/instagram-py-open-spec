"""StoryService handles story creation, retrieval, viewing, and cleanup."""

import random
from uuid import UUID

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.posts.models import Story, StoryView
from apps.social.services import FollowService


class StoryService:
    """Service for managing stories and story views."""

    @staticmethod
    def _generate_placeholder_image() -> SimpleUploadedFile:
        color = random.randint(0, 0xFFFFFF)
        gif_data = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9"
            b"\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
            b"\x00\x02\x02\x4c\x01\x00\x3b"
        )
        return SimpleUploadedFile(
            f"story_{color}.jpg",
            gif_data,
            content_type="image/jpeg",
        )

    def create(self, owner_id: UUID, media_type: str = "image") -> Story:
        file = self._generate_placeholder_image()
        story = Story.objects.create(
            owner_id=owner_id,
            file=file,
            media_type=media_type,
        )
        return story

    @staticmethod
    def get_active_for_user(user_id: UUID) -> list[Story]:
        now = timezone.now()
        return list(
            Story.objects.filter(owner_id=user_id, expires_at__gt=now)
            .select_related("owner")
            .order_by("-created_at")
        )

    @staticmethod
    def get_feed_stories(user_id: UUID) -> list[dict]:
        now = timezone.now()
        following_ids = FollowService.get_following(user_id).values_list(
            "id", flat=True
        )

        stories = (
            Story.objects.filter(
                owner_id__in=following_ids,
                expires_at__gt=now,
            )
            .select_related("owner")
            .order_by("owner_id", "-created_at")
        )

        grouped: dict[UUID, dict] = {}
        for story in stories:
            oid = story.owner.id  # type: ignore[attr-defined]
            if oid not in grouped:
                grouped[oid] = {
                    "user": story.owner,
                    "stories": [],
                }
            story.is_viewed = StoryView.objects.filter(  # type: ignore[attr-defined]
                story_id=story.id,
                viewer_id=user_id,
            ).exists()
            grouped[oid]["stories"].append(story)

        unviewed = [g for g in grouped.values() if not g["stories"][0].is_viewed]
        viewed = [g for g in grouped.values() if g["stories"][0].is_viewed]
        return unviewed + viewed

    @staticmethod
    def mark_viewed(story_id: UUID, viewer_id: UUID) -> bool:
        _, created = StoryView.objects.get_or_create(
            story_id=story_id,
            viewer_id=viewer_id,
        )
        return created

    @staticmethod
    def is_viewed(story_id: UUID, viewer_id: UUID) -> bool:
        return StoryView.objects.filter(
            story_id=story_id,
            viewer_id=viewer_id,
        ).exists()

    @staticmethod
    def get_by_id(story_id: UUID) -> Story | None:
        try:
            return Story.objects.select_related("owner").get(pk=story_id)
        except Story.DoesNotExist:
            return None

    @staticmethod
    def cleanup_expired() -> int:
        now = timezone.now()
        expired_ids = list(
            Story.objects.filter(expires_at__lt=now).values_list("pk", flat=True)
        )
        Story.objects.filter(pk__in=expired_ids).delete()
        return len(expired_ids)
