from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import PostService


@dataclass(frozen=True, slots=True)
class GetPostInput:
    post_id: UUID


@dataclass(frozen=True, slots=True)
class GetPostOutput:
    success: bool
    post: object | None = None
    error: str | None = None


class GetPostUseCase:
    def __init__(self, post_service: PostService):
        self._post_service = post_service

    def execute(self, input_dto: GetPostInput) -> GetPostOutput:
        post = self._post_service.get_by_id(input_dto.post_id)
        if not post:
            return GetPostOutput(success=False, error="Post not found")
        return GetPostOutput(success=True, post=post)
