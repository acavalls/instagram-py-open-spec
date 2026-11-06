from dataclasses import dataclass
from uuid import UUID

from apps.posts.services import StoryService
from apps.social.services import FollowService


@dataclass(frozen=True, slots=True)
class ViewStoryInput:
    story_id: UUID
    viewer_id: UUID


@dataclass(frozen=True, slots=True)
class ViewStoryOutput:
    success: bool
    error: str | None = None


class ViewStoryUseCase:
    def __init__(
        self,
        story_service: StoryService,
        follow_service: FollowService | None = None,
    ):
        self._story_service = story_service
        self._follow_service = follow_service or FollowService()

    def execute(self, input_dto: ViewStoryInput) -> ViewStoryOutput:
        story = self._story_service.get_by_id(input_dto.story_id)
        if story is None:
            return ViewStoryOutput(success=False, error="Story not found")

        if story.is_expired():
            return ViewStoryOutput(success=False, error="Story has expired")

        if story.owner_id == input_dto.viewer_id:  # type: ignore[attr-defined]
            return ViewStoryOutput(
                success=False, error="You cannot view your own story"
            )

        if not self._follow_service.is_following(
            input_dto.viewer_id, story.owner_id  # type: ignore[attr-defined]
        ):
            return ViewStoryOutput(
                success=False, error="You can only view stories from users you follow"
            )

        self._story_service.mark_viewed(
            story_id=input_dto.story_id,
            viewer_id=input_dto.viewer_id,
        )
        return ViewStoryOutput(success=True)
