"""Follow user use case."""

from dataclasses import dataclass
from uuid import UUID

from apps.social.services.follow_service import FollowService


@dataclass(frozen=True, slots=True)
class FollowUserInput:
    follower_id: UUID
    following_id: UUID


@dataclass(frozen=True, slots=True)
class FollowUserOutput:
    success: bool
    error: str | None = None


class FollowUserUseCase:
    """Follows a user after validating the relationship."""

    def __init__(self, follow_service: FollowService):
        self._follow_service = follow_service

    def execute(self, input_dto: FollowUserInput) -> FollowUserOutput:
        success, error = self._follow_service.follow(
            input_dto.follower_id, input_dto.following_id
        )
        if success:
            return FollowUserOutput(success=True)
        return FollowUserOutput(success=False, error=error)
