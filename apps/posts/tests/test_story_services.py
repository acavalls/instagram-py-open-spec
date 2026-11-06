"""Tests for StoryService feed grouping, view marking and cleanup.

Scenarios: Bar lists followed users with active stories, Bar excludes
non-followed users, Unviewed groups first, First view recorded, Repeated
view is idempotent, Lazy purge on home render (spec delta: stories)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.services import StoryService
from apps.posts.tests.factories import StoryFactory, StoryViewFactory
from apps.social.services import FollowService
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestStoryServiceFeed:
    def test_bar_lists_followed_users_with_active_stories(self):
        """Scenario: Bar lists followed users with active stories."""
        viewer = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=viewer, following=followed)
        story = StoryFactory(owner=followed)

        groups = StoryService.get_feed_stories(viewer.id)

        assert len(groups) == 1
        assert groups[0]["user"].id == followed.id
        assert [s.id for s in groups[0]["stories"]] == [story.id]
        assert groups[0]["stories"][0].is_viewed is False

    def test_bar_excludes_non_followed_users(self):
        """Scenario: Bar excludes non-followed users."""
        viewer = UserFactory()
        stranger = UserFactory()
        StoryFactory(owner=stranger)

        groups = StoryService.get_feed_stories(viewer.id)

        assert groups == []

    def test_unviewed_groups_first(self):
        """Scenario: Unviewed groups first."""
        viewer = UserFactory()
        seen_author = UserFactory()
        unseen_author = UserFactory()
        FollowFactory(follower=viewer, following=seen_author)
        FollowFactory(follower=viewer, following=unseen_author)
        seen_story = StoryFactory(owner=seen_author)
        StoryViewFactory(story=seen_story, viewer=viewer)
        unseen_story = StoryFactory(owner=unseen_author)

        groups = StoryService.get_feed_stories(viewer.id)

        assert [g["user"].id for g in groups] == [unseen_author.id, seen_author.id]
        assert groups[0]["stories"][0].id == unseen_story.id

    def test_groups_ordered_newest_first_within_group(self):
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        older = StoryFactory(owner=author)
        newer = StoryFactory(owner=author)

        groups = StoryService.get_feed_stories(viewer.id)

        assert [s.id for s in groups[0]["stories"]] == [newer.id, older.id]

    def test_group_latest_story_viewed_goes_last(self):
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        story = StoryFactory(owner=author)
        StoryViewFactory(story=story, viewer=viewer)

        groups = StoryService.get_feed_stories(viewer.id)

        assert len(groups) == 1
        assert groups[0]["stories"][0].is_viewed is True

    def test_expired_stories_excluded_from_feed(self):
        viewer = UserFactory()
        author = UserFactory()
        FollowFactory(follower=viewer, following=author)
        StoryFactory(owner=author, expires_at=timezone.now() - timedelta(hours=1))

        assert StoryService.get_feed_stories(viewer.id) == []


class TestStoryServiceViews:
    def test_first_view_recorded(self):
        """Scenario: First view recorded."""
        viewer = UserFactory()
        story = StoryFactory(owner=UserFactory())

        created = StoryService.mark_viewed(story.id, viewer.id)

        assert created is True
        assert StoryService.is_viewed(story.id, viewer.id)

    def test_repeated_view_is_idempotent(self):
        """Scenario: Repeated view is idempotent."""
        viewer = UserFactory()
        story = StoryFactory(owner=UserFactory())
        StoryService.mark_viewed(story.id, viewer.id)

        created = StoryService.mark_viewed(story.id, viewer.id)

        assert created is False
        assert story.views.count() == 1


class TestStoryServiceCleanup:
    def test_lazy_purge_deletes_expired_stories_and_views(self):
        """Scenario: Lazy purge on home render (service part)."""
        viewer = UserFactory()
        expired = StoryFactory(
            owner=UserFactory(),
            expires_at=timezone.now() - timedelta(hours=1),
        )
        StoryViewFactory(story=expired, viewer=viewer)
        active = StoryFactory(owner=UserFactory())

        deleted = StoryService.cleanup_expired()

        assert deleted == 1
        assert not StoryService.get_by_id(expired.id)
        assert StoryService.get_by_id(active.id)

    def test_get_by_id_unknown_returns_none(self):
        import uuid

        assert StoryService.get_by_id(uuid.uuid4()) is None


class TestStoryServiceFollowIntegration:
    def test_follow_service_integration_lists_followee_stories(self):
        viewer = UserFactory()
        author = UserFactory()
        assert not FollowService.is_following(viewer.id, author.id)
        StoryFactory(owner=author)
        assert StoryService.get_feed_stories(viewer.id) == []
        FollowFactory(follower=viewer, following=author)
        assert len(StoryService.get_feed_stories(viewer.id)) == 1
