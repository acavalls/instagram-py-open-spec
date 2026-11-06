from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import StoryService


@dataclass(frozen=True, slots=True)
class CreateStoryInput:
    owner_id: UUID
    media_type: str = "image"


@dataclass(frozen=True, slots=True)
class CreateStoryOutput:
    success: bool
    story_id: UUID | None = None
    error: str | None = None


class CreateStoryUseCase:
    def __init__(self, story_service: StoryService):
        self._story_service = story_service

    def execute(self, input_dto: CreateStoryInput) -> CreateStoryOutput:
        story = self._story_service.create(
            owner_id=input_dto.owner_id,
            media_type=input_dto.media_type,
        )
        return CreateStoryOutput(success=True, story_id=story.id)
