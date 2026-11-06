"""Get user suggestions use case."""

from dataclasses import dataclass
from uuid import UUID

from apps.accounts.models import User
from apps.social.services.feed_service import FeedService


@dataclass(frozen=True, slots=True)
class GetUserSuggestionsInput:
    user_id: UUID
    limit: int = 5


@dataclass(frozen=True, slots=True)
class GetUserSuggestionsOutput:
    success: bool
    users: list[User] | None = None
    error: str | None = None


class GetUserSuggestionsUseCase:
    """Returns user suggestions for users not already followed."""

    def __init__(self, feed_service: FeedService):
        self._feed_service = feed_service

    def execute(self, input_dto: GetUserSuggestionsInput) -> GetUserSuggestionsOutput:
        suggestions = self._feed_service.get_suggestions(
            input_dto.user_id, input_dto.limit
        )
        return GetUserSuggestionsOutput(success=True, users=list(suggestions))
