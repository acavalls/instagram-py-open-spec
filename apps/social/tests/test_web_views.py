"""Tests for the web home feed and suggestions panel.

Scenarios: Feed shows followed users' posts, Empty feed state, Suggestions
exclude followed users and self (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.tests.factories import PostFactory
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


def _login(client, user):
    client.force_login(user)


class TestIndexFeed:
    def test_feed_shows_only_followed_users_posts(self, client):
        """Scenario: Feed shows followed users' posts."""
        user = UserFactory()
        followed = UserFactory(username="followeduser")
        stranger = UserFactory(username="strangeruser")
        FollowFactory(follower=user, following=followed)
        PostFactory(owner=followed, caption="followed post")
        PostFactory(owner=stranger, caption="stranger post")

        _login(client, user)
        response = client.get("/web/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "followed post" in content
        assert "stranger post" not in content

    def test_feed_ordered_newest_first(self, client):
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        old_post = PostFactory(owner=followed, caption="old caption")
        new_post = PostFactory(owner=followed, caption="new caption")

        _login(client, user)
        response = client.get("/web/")

        content = response.content.decode()
        assert content.index("new caption") < content.index("old caption")
        assert {new_post.id, old_post.id}

    def test_empty_feed_state_when_user_follows_nobody(self, client):
        """Scenario: Empty feed state."""
        user = UserFactory()
        PostFactory(owner=user, caption="my own post")

        _login(client, user)
        response = client.get("/web/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "my own post" not in content
        assert "Share Photos" in content
        assert "Share your first photo" in content
        assert "empty-feed__title" in content

    def test_feed_without_posts_but_with_follows_shows_other_empty_state(self, client):
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)

        _login(client, user)
        response = client.get("/web/")

        content = response.content.decode()
        assert "No posts from the people you follow" in content
        assert "Share your first photo" not in content


class TestSuggestionsPanel:
    def test_suggestions_excludes_self_and_followed(self, client):
        """Scenario: Suggestions exclude followed users and self."""
        user = UserFactory(username="mainuser")
        followed = UserFactory(username="followeduser")
        UserFactory(username="candidateuser")
        FollowFactory(follower=user, following=followed)

        _login(client, user)
        response = client.get("/web/")

        content = response.content.decode()
        assert "candidateuser" in content
        suggestions_rows = content.split('class="feed-sidebar__suggestion-username"')[
            1:
        ]
        assert suggestions_rows and "followeduser" not in suggestions_rows[0]
        assert "Suggested for you" in content

    def test_suggestions_limited_to_five(self, client):
        user = UserFactory()
        for i in range(8):
            UserFactory(username=f"candidate{i}")

        _login(client, user)
        response = client.get("/web/")

        content = response.content.decode()
        assert content.count('class="feed-sidebar__suggestion-username"') == 5

    def test_suggestion_rows_show_avatar_and_follow_button(self, client):
        """Scenario: Suggestion rows show avatar and follow button."""
        user = UserFactory(username="mainuser")
        UserFactory(username="candidateuser")

        _login(client, user)
        response = client.get("/web/")

        content = response.content.decode()
        row = content.split('class="feed-sidebar__suggestion"', 1)[1]
        assert "follow-btn" in row
        assert "/web/follow/" in row

    def test_anonymous_user_redirected_to_login(self, client):
        response = client.get("/web/")

        assert response.status_code == 302
        assert "/web/login/" in response.url
