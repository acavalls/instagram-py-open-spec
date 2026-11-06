"""Tests for FeedService — feed aggregation and suggestions.

Scenarios: Feed shows followed users' posts, Feed ordered newest first with
pagination, Suggestions exclude followed users and self, Suggestions limited
to newest accounts (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.tests.factories import PostFactory
from apps.social.services import FeedService
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def feed_service():
    return FeedService()


class TestListFeed:
    def test_feed_shows_only_followed_users_posts_newest_first(self, feed_service):
        """Scenario: Feed shows followed users' posts."""
        user = UserFactory()
        followed = UserFactory()
        stranger = UserFactory()
        FollowFactory(follower=user, following=followed)
        old_post = PostFactory(owner=followed)
        new_post = PostFactory(owner=followed)
        PostFactory(owner=stranger)
        PostFactory(owner=user)

        posts = list(feed_service.list_feed(user.id))

        assert [p.id for p in posts] == [new_post.id, old_post.id]

    def test_feed_pagination_window_without_duplicates(self, feed_service):
        """Scenario: Feed ordered newest first with pagination."""
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        posts = [PostFactory(owner=followed) for _ in range(5)]

        page1 = list(feed_service.list_feed(user.id, limit=2, offset=0))
        page2 = list(feed_service.list_feed(user.id, limit=2, offset=2))

        page1_ids = {p.id for p in page1}
        page2_ids = {p.id for p in page2}
        assert len(page1) == 2
        assert len(page2) == 2
        assert not page1_ids & page2_ids
        expected = {p.id for p in (posts[1], posts[2], posts[3], posts[4])}
        assert {p.id for p in page1 + page2} == expected


class TestGetSuggestions:
    def test_suggestions_exclude_self_and_followed(self, feed_service):
        """Scenario: Suggestions exclude followed users and self."""
        user = UserFactory()
        followed = UserFactory()
        candidate = UserFactory()
        FollowFactory(follower=user, following=followed)

        suggestions = list(feed_service.get_suggestions(user.id))

        assert candidate in suggestions
        assert user not in suggestions
        assert followed not in suggestions

    def test_suggestions_limited_to_five_newest_accounts(self, feed_service):
        """Scenario: Suggestions limited to newest accounts."""
        user = UserFactory()
        candidates = [UserFactory(username=f"candidate{i}") for i in range(8)]

        suggestions = list(feed_service.get_suggestions(user.id, limit=5))

        assert len(suggestions) == 5
        assert {c.id for c in suggestions} == {c.id for c in candidates[3:]}
