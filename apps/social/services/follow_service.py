"""Follow service — domain logic for follow relationships."""

from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from apps.accounts.models import User
from apps.social.models import Follow


class FollowService:
    """Service for follow-related business logic."""

    def follow(self, follower_id: UUID, following_id: UUID) -> tuple[bool, str]:
        """Create a follow relationship. Returns (success, error_message)."""
        if follower_id == following_id:
            return False, "You cannot follow yourself"

        try:
            with transaction.atomic():
                Follow.objects.create(
                    follower_id=follower_id, following_id=following_id
                )
            return True, ""
        except IntegrityError:
            return False, "Already following this user"

    def unfollow(self, follower_id: UUID, following_id: UUID) -> tuple[bool, str]:
        """Remove a follow relationship. Returns (success, error_message)."""
        deleted, _ = Follow.objects.filter(
            follower_id=follower_id, following_id=following_id
        ).delete()
        if deleted:
            return True, ""
        return False, "Follow relationship not found"

    @staticmethod
    def is_following(follower_id: UUID, following_id: UUID) -> bool:
        """Check if a user is following another user."""
        return Follow.objects.filter(
            follower_id=follower_id, following_id=following_id
        ).exists()

    @staticmethod
    def is_following_anyone(user_id: UUID) -> bool:
        """Check if a user follows at least one other user."""
        return Follow.objects.filter(follower_id=user_id).exists()

    @staticmethod
    def get_following(user_id: UUID) -> QuerySet[User]:
        """Get all users that a user is following."""
        return User.objects.filter(followers__follower_id=user_id).order_by("username")

    @staticmethod
    def get_followers(user_id: UUID) -> QuerySet[User]:
        """Get all followers of a user."""
        return User.objects.filter(following__following_id=user_id).order_by("username")
