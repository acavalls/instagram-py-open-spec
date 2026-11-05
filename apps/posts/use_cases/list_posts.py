from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import PostService


@dataclass(frozen=True, slots=True)
class ListPostsInput:
    user_id: UUID
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True, slots=True)
class ListPostsOutput:
    success: bool
    posts: list | None = None
    error: str | None = None


class ListPostsUseCase:
    def __init__(self, post_service: PostService):
        self._post_service = post_service

    def execute(self, input_dto: ListPostsInput) -> ListPostsOutput:
        posts = list(
            self._post_service.list_for_user(
                user_id=input_dto.user_id,
                limit=input_dto.limit,
                offset=input_dto.offset,
            )
        )
        return ListPostsOutput(success=True, posts=posts)
