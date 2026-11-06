from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import StoryService


@dataclass(frozen=True, slots=True)
class ListFeedStoriesInput:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class ListFeedStoriesOutput:
    success: bool
    stories_grouped_by_user: list[dict] | None = None
    error: str | None = None


class ListFeedStoriesUseCase:
    def __init__(self, story_service: StoryService):
        self._story_service = story_service

    def execute(self, input_dto: ListFeedStoriesInput) -> ListFeedStoriesOutput:
        stories = self._story_service.get_feed_stories(user_id=input_dto.user_id)
        return ListFeedStoriesOutput(success=True, stories_grouped_by_user=stories)
