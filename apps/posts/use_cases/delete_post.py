from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import PostService


@dataclass(frozen=True, slots=True)
class DeletePostInput:
    post_id: UUID
    user_id: UUID


@dataclass(frozen=True, slots=True)
class DeletePostOutput:
    success: bool
    error: str | None = None


class DeletePostUseCase:
    def __init__(self, post_service: PostService):
        self._post_service = post_service

    def execute(self, input_dto: DeletePostInput) -> DeletePostOutput:
        post = self._post_service.get_by_id(input_dto.post_id)
        if not post:
            return DeletePostOutput(success=False, error="Post not found")

        is_valid, error = post.can_delete(input_dto.user_id)
        if not is_valid:
            return DeletePostOutput(success=False, error=error)

        self._post_service.delete(post)
        return DeletePostOutput(success=True)
