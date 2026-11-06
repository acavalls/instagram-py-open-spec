"""Tests for story use cases (CreateStory, ListFeedStories, ViewStory).

Scenarios: Self-view rejected, Non-followed story not viewable, First view
recorded, Expired story not viewable (spec delta: stories)."""

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.services import StoryService
from apps.posts.tests.factories import StoryFactory
from apps.posts.use_cases import (
    CreateStoryInput,
    CreateStoryUseCase,
    ListFeedStoriesInput,
    ListFeedStoriesUseCase,
    ViewStoryInput,
    ViewStoryUseCase,
)
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestCreateStoryUseCase:
    def test_creates_story_with_placeholder_media(self):
        user = UserFactory()

        output = CreateStoryUseCase(story_service=StoryService()).execute(
            CreateStoryInput(owner_id=user.id)
        )

        assert output.success
        assert output.story_id == user.stories.first().id


class TestListFeedStoriesUseCase:
    def test_returns_groups_for_followees(self):
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        StoryFactory(owner=author)

        output = ListFeedStoriesUseCase(story_service=StoryService()).execute(
            ListFeedStoriesInput(user_id=viewer.id)
        )

        assert output.success
        assert len(output.stories_grouped_by_user) == 1
        assert output.stories_grouped_by_user[0]["user"].id == author.id


class TestViewStoryUseCase:
    def test_records_view_for_followed_author(self):
        """Scenario: First view recorded."""
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        story = StoryFactory(owner=author)

        output = ViewStoryUseCase(story_service=StoryService()).execute(
            ViewStoryInput(story_id=story.id, viewer_id=viewer.id)
        )

        assert output.success
        assert StoryService.is_viewed(story.id, viewer.id)

    def test_rejects_self_view(self):
        """Scenario: Self-view rejected."""
        user = UserFactory()
        story = StoryFactory(owner=user)

        output = ViewStoryUseCase(story_service=StoryService()).execute(
            ViewStoryInput(story_id=story.id, viewer_id=user.id)
        )

        assert not output.success
        assert output.error == "You cannot view your own story"
        assert not StoryService.is_viewed(story.id, user.id)

    def test_rejects_non_followed_author(self):
        """Scenario: Non-followed story not viewable."""
        viewer = UserFactory()
        stranger = UserFactory()
        story = StoryFactory(owner=stranger)

        output = ViewStoryUseCase(story_service=StoryService()).execute(
            ViewStoryInput(story_id=story.id, viewer_id=viewer.id)
        )

        assert not output.success
        assert not StoryService.is_viewed(story.id, viewer.id)

    def test_rejects_unknown_story(self):
        viewer = UserFactory()

        output = ViewStoryUseCase(story_service=StoryService()).execute(
            ViewStoryInput(story_id=uuid.uuid4(), viewer_id=viewer.id)
        )

        assert not output.success
        assert output.error == "Story not found"

    def test_rejects_expired_story(self):
        """Scenario: Expired story not viewable."""
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        story = StoryFactory(
            owner=author,
            expires_at=timezone.now() - timedelta(hours=1),
        )

        output = ViewStoryUseCase(story_service=StoryService()).execute(
            ViewStoryInput(story_id=story.id, viewer_id=viewer.id)
        )

        assert not output.success
        assert output.error == "Story has expired"
        assert not StoryService.is_viewed(story.id, viewer.id)
