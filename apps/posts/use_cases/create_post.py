from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import PostService


@dataclass(frozen=True, slots=True)
class CreatePostInput:
    owner_id: UUID
    caption: str
    media_files: list[dict] | None = None


@dataclass(frozen=True, slots=True)
class CreatePostOutput:
    success: bool
    post_id: UUID | None = None
    error: str | None = None


class CreatePostUseCase:
    def __init__(self, post_service: PostService):
        self._post_service = post_service

    def execute(self, input_dto: CreatePostInput) -> CreatePostOutput:
        post = self._post_service.create(
            owner_id=input_dto.owner_id,
            caption=input_dto.caption,
            media_files=input_dto.media_files,
        )
        return CreatePostOutput(success=True, post_id=post.id)
