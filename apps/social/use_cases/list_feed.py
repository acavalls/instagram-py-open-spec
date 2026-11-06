"""List feed posts use case — posts from followed users."""

from dataclasses import dataclass
from uuid import UUID

from apps.posts.models import Post
from apps.social.services.feed_service import FeedService


@dataclass(frozen=True, slots=True)
class ListFeedInput:
    user_id: UUID
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True, slots=True)
class ListFeedOutput:
    success: bool
    posts: list[Post] | None = None
    error: str | None = None


class ListFeedUseCase:
    """Lists posts from users that the current user follows."""

    def __init__(self, feed_service: FeedService):
        self._feed_service = feed_service

    def execute(self, input_dto: ListFeedInput) -> ListFeedOutput:
        posts = list(
            self._feed_service.list_feed(
                user_id=input_dto.user_id,
                limit=input_dto.limit,
                offset=input_dto.offset,
            )
        )
        return ListFeedOutput(success=True, posts=posts)
