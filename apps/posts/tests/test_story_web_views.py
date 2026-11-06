"""Tests for story web views (HTMX) and the home stories bar.

Scenarios: Successful web creation, Unauthenticated creation rejected,
Bar lists followed users with active stories, Bar excludes non-followed
users, Bar empty without followings, First view recorded, Repeated view
is idempotent, Self-view rejected, Non-followed story not viewable,
Unviewed groups first, Ring updates after viewing, Lazy purge on home
render, Management command cleanup (spec delta: stories)."""

import uuid
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import StoryView
from apps.posts.services import StoryService
from apps.posts.tests.factories import StoryFactory, StoryViewFactory
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestStoryCreationView:
    def test_successful_web_creation(self, client):
        """Scenario: Successful web creation."""
        user = UserFactory()
        client.force_login(user)

        response = client.post("/web/stories/create/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Story created" in content
        assert 'hx-swap-oob' in content
        assert user.stories.count() == 1
        assert user.stories.first().file.name.startswith("stories/")

    def test_unauthenticated_creation_rejected(self, client):
        """Scenario: Unauthenticated creation rejected."""
        response = client.post("/web/stories/create/")

        assert response.status_code == 302
        assert "/web/login/" in response.url
        assert StoryView.objects.count() == 0


class TestStoriesBarOnHomePage:
    def test_bar_lists_followed_users_with_active_stories(self, client):
        """Scenario: Bar lists followed users with active stories."""
        user = UserFactory()
        followed = UserFactory(username="storyauthor")
        FollowFactory(follower=user, following=followed)
        StoryFactory(owner=followed)
        client.force_login(user)

        response = client.get("/web/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Your story" in content
        assert "storyauthor" in content
        assert "stories__avatar--unseen" in content

    def test_bar_excludes_non_followed_users(self, client):
        """Scenario: Bar excludes non-followed users."""
        user = UserFactory()
        stranger = UserFactory(username="stranger")
        StoryFactory(owner=stranger)
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        bar = content.split('id="stories-bar"', 1)[1].split("</section>", 1)[0]
        assert "stranger" not in bar

    def test_bar_empty_without_followings(self, client):
        """Scenario: Bar empty without followings."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        assert "Your story" in content
        assert "stories__avatar--unseen" not in content
        assert "stories__avatar--viewed" not in content


class TestStoryViewTracking:
    def test_first_view_recorded(self, client):
        """Scenario: First view recorded."""
        user = UserFactory()
        author = UserFactory()
        FollowFactory(follower=user, following=author)
        story = StoryFactory(owner=author)
        client.force_login(user)

        response = client.post(f"/web/stories/{story.id}/view/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Story viewed" in content
        assert StoryService.is_viewed(story.id, user.id)

    def test_repeated_view_is_idempotent(self, client):
        """Scenario: Repeated view is idempotent."""
        user = UserFactory()
        author = UserFactory()
        FollowFactory(follower=user, following=author)
        story = StoryFactory(owner=author)
        client.force_login(user)

        client.post(f"/web/stories/{story.id}/view/")
        response = client.post(f"/web/stories/{story.id}/view/")

        assert response.status_code == 200
        assert StoryView.objects.filter(story=story, viewer=user).count() == 1

    def test_self_view_rejected(self, client):
        """Scenario: Self-view rejected."""
        user = UserFactory()
        story = StoryFactory(owner=user)
        client.force_login(user)

        response = client.post(f"/web/stories/{story.id}/view/")

        assert response.status_code == 200
        assert "cannot view your own story" in response.content.decode()
        assert not StoryView.objects.filter(story=story, viewer=user).exists()

    def test_non_followed_story_not_viewable(self, client):
        """Scenario: Non-followed story not viewable."""
        user = UserFactory()
        stranger = UserFactory()
        story = StoryFactory(owner=stranger)
        client.force_login(user)

        response = client.post(f"/web/stories/{story.id}/view/")

        assert response.status_code == 200
        assert "users you follow" in response.content.decode()
        assert not StoryView.objects.filter(story=story, viewer=user).exists()

    def test_unknown_story_rejected(self, client):
        user = UserFactory()
        client.force_login(user)

        response = client.post(f"/web/stories/{uuid.uuid4()}/view/")

        assert response.status_code == 200
        assert "Story not found" in response.content.decode()


class TestStoriesBarOrdering:
    def test_unviewed_groups_first(self, client):
        """Scenario: Unviewed groups first."""
        user = UserFactory()
        seen_author = UserFactory(username="seenauthor")
        unseen_author = UserFactory(username="unseenauthor")
        FollowFactory(follower=user, following=seen_author)
        FollowFactory(follower=user, following=unseen_author)
        seen_story = StoryFactory(owner=seen_author)
        StoryFactory(owner=unseen_author)
        StoryViewFactory(story=seen_story, viewer=user)
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        assert content.index("unseenauthor") < content.index("seenauthor")

    def test_ring_updates_after_viewing(self, client):
        """Scenario: Ring updates after viewing."""
        user = UserFactory()
        author = UserFactory(username="ringauthor")
        FollowFactory(follower=user, following=author)
        story = StoryFactory(owner=author)
        client.force_login(user)

        client.post(f"/web/stories/{story.id}/view/")
        response = client.get("/web/")

        content = response.content.decode()
        assert "stories__avatar--viewed" in content
        assert "stories__avatar--unseen" not in content


class TestExpiredStoryCleanup:
    def test_lazy_purge_on_home_render(self, client):
        """Scenario: Lazy purge on home render."""
        user = UserFactory()
        expired = StoryFactory(
            owner=UserFactory(),
            expires_at=timezone.now() - timedelta(hours=1),
        )
        StoryViewFactory(story=expired, viewer=user)
        client.force_login(user)

        response = client.get("/web/")

        assert response.status_code == 200
        assert not StoryView.objects.filter(story=expired).exists()

    def test_management_command_cleanup(self, capsys):
        """Scenario: Management command cleanup."""
        expired = StoryFactory(
            owner=UserFactory(),
            expires_at=timezone.now() - timedelta(hours=1),
        )
        StoryViewFactory(story=expired, viewer=UserFactory())
        StoryFactory(owner=UserFactory())

        call_command("cleanup_expired_stories")

        out = capsys.readouterr().out
        assert "Deleted 1 expired story(ies)" in out
