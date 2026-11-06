"""Tests for Story and StoryView models and StoryService.

Scenarios: Story persisted with placeholder media, Expired story is not
active (spec delta: stories, Story data model)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import Story
from apps.posts.services import StoryService
from apps.posts.tests.factories import StoryFactory

pytestmark = pytest.mark.django_db


class TestStoryDataModel:
    def test_story_persisted_with_placeholder_media(self):
        """Scenario: Story persisted with placeholder media."""
        user = UserFactory()

        story = StoryService().create(user.id)

        assert story.owner_id == user.id
        assert story.file.name.startswith("stories/")
        assert "/".join(story.file.name.split("/")[1:4]) == (
            f"{timezone.now().year}/{timezone.now().month:02d}/{timezone.now().day:02d}"
        )
        assert story.media_type == Story.MediaType.IMAGE
        assert not story.is_expired()
        delta = story.expires_at - story.created_at
        assert abs(delta - timedelta(hours=24)) < timedelta(seconds=1)

    def test_expired_story_is_not_active(self):
        """Scenario: Expired story is not active."""
        user = UserFactory()
        StoryFactory(
            owner=user,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        active = StoryFactory(owner=user)

        active_stories = StoryService.get_active_for_user(user.id)

        assert active in active_stories
        assert len(active_stories) == 1
