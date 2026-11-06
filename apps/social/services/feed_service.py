"""Feed service — content aggregation from followed users."""

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.posts.models import Post
from apps.social.models import Follow


class FeedService:
    """Service for feed and discovery operations."""

    @staticmethod
    def list_feed(
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> QuerySet[Post]:
        """Get posts from users that the given user follows."""
        following_ids = Follow.objects.filter(follower_id=user_id).values_list(
            "following_id", flat=True
        )
        return (
            Post.objects.filter(owner_id__in=following_ids)
            .select_related("owner")
            .prefetch_related("media")
            .order_by("-created_at")[offset : offset + limit]
        )

    @staticmethod
    def get_suggestions(user_id: UUID, limit: int = 5) -> QuerySet[User]:
        """Get user suggestions: users not already followed, ordered by recent."""
        following_ids = Follow.objects.filter(follower_id=user_id).values_list(
            "following_id", flat=True
        )
        return (
            User.objects.exclude(id__in=following_ids)
            .exclude(id=user_id)
            .order_by("-date_joined")[:limit]
        )
