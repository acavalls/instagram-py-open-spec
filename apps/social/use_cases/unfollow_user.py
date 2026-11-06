"""Unfollow user use case."""

from dataclasses import dataclass
from uuid import UUID

from apps.social.services.follow_service import FollowService


@dataclass(frozen=True, slots=True)
class UnfollowUserInput:
    follower_id: UUID
    following_id: UUID


@dataclass(frozen=True, slots=True)
class UnfollowUserOutput:
    success: bool
    error: str | None = None


class UnfollowUserUseCase:
    """Unfollows a user."""

    def __init__(self, follow_service: FollowService):
        self._follow_service = follow_service

    def execute(self, input_dto: UnfollowUserInput) -> UnfollowUserOutput:
        success, error = self._follow_service.unfollow(
            input_dto.follower_id, input_dto.following_id
        )
        if success:
            return UnfollowUserOutput(success=True)
        return UnfollowUserOutput(success=False, error=error)
