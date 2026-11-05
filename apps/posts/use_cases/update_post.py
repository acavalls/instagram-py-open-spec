from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import PostService


@dataclass(frozen=True, slots=True)
class UpdatePostInput:
    post_id: UUID
    user_id: UUID
    caption: str


@dataclass(frozen=True, slots=True)
class UpdatePostOutput:
    success: bool
    post_id: UUID | None = None
    error: str | None = None


class UpdatePostUseCase:
    def __init__(self, post_service: PostService):
        self._post_service = post_service

    def execute(self, input_dto: UpdatePostInput) -> UpdatePostOutput:
        post = self._post_service.get_by_id(input_dto.post_id)
        if not post:
            return UpdatePostOutput(success=False, error="Post not found")

        is_valid, error = post.can_edit(input_dto.user_id)
        if not is_valid:
            return UpdatePostOutput(success=False, error=error)

        updated = self._post_service.update_caption(post, input_dto.caption)
        return UpdatePostOutput(success=True, post_id=updated.id)
