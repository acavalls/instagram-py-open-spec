"""Tests for the web profile page and following list modal.

Scenarios: Own profile shows stats and editable grid, Other user profile
shows stats and follow state, Unknown profile responds 404, Following list
shows followed users, Following list search filters (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.tests.factories import PostFactory
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestProfileView:
    def test_own_profile_shows_stats_and_editable_grid(self, client):
        """Scenario: Own profile shows stats and editable grid."""
        user = UserFactory()
        post = PostFactory(owner=user, caption="my post")

        client.force_login(user)
        response = client.get(f"/web/profile/{user.id}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert f"@{user.username}" in content
        assert "1</strong> posts" in content
        assert "my post" in content
        assert f"post-{post.id}" in content
        assert "Edit" in content

    def test_other_profile_shows_stats_and_follow_state(self, client):
        """Scenario: Other user profile shows stats and follow state."""
        user = UserFactory()
        other = UserFactory(username="otheruser")
        PostFactory(owner=other, caption="other post")

        client.force_login(user)
        response = client.get(f"/web/profile/{other.id}/")

        content = response.content.decode()
        assert "other post" in content
        assert "follow-btn--follow" in content
        assert "Edit" not in content

    def test_other_profile_following_shows_unfollow_state(self, client):
        user = UserFactory()
        other = UserFactory()
        FollowFactory(follower=user, following=other)

        client.force_login(user)
        response = client.get(f"/web/profile/{other.id}/")

        content = response.content.decode()
        assert "follow-btn--unfollow" in content

    def test_unknown_profile_responds_404(self, client):
        """Scenario: Unknown profile responds 404."""
        user = UserFactory()

        client.force_login(user)
        response = client.get("/web/profile/00000000-0000-0000-0000-000000000000/")

        assert response.status_code == 404

    def test_profile_grid_paginates(self, client):
        user = UserFactory()
        for i in range(15):
            PostFactory(owner=user, caption=f"post {i}")

        client.force_login(user)
        response = client.get(f"/web/profile/{user.id}/")

        content = response.content.decode()
        assert content.count('<article class="post-card"') == 12
        assert "Older" in content

    def test_profile_requires_login(self, client):
        user = UserFactory()

        response = client.get(f"/web/profile/{user.id}/")

        assert response.status_code == 302
        assert "/web/login/" in response.url


class TestFollowingListView:
    def test_following_list_shows_followed_users(self, client):
        """Scenario: Following list shows followed users."""
        user = UserFactory()
        followed_a = UserFactory(username="alice")
        followed_b = UserFactory(username="bob")
        UserFactory(username="stranger")
        FollowFactory(follower=user, following=followed_a)
        FollowFactory(follower=user, following=followed_b)

        client.force_login(user)
        response = client.get(f"/web/profile/{user.id}/following/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "alice" in content
        assert "bob" in content
        assert "stranger" not in content

    def test_following_list_search_filters_by_username(self, client):
        """Scenario: Following list search filters."""
        user = UserFactory()
        followed_a = UserFactory(username="alice")
        followed_b = UserFactory(username="bob")
        FollowFactory(follower=user, following=followed_a)
        FollowFactory(follower=user, following=followed_b)

        client.force_login(user)
        response = client.get(f"/web/profile/{user.id}/following/", {"q": "ali"})

        content = response.content.decode()
        assert "alice" in content
        assert "bob" not in content

    def test_following_list_search_filters_by_name(self, client):
        user = UserFactory()
        followed = UserFactory(username="xyz", first_name="Alice")
        FollowFactory(follower=user, following=followed)

        client.force_login(user)
        response = client.get(f"/web/profile/{user.id}/following/", {"q": "Alice"})

        content = response.content.decode()
        assert "xyz" in content

    def test_unknown_user_following_list_responds_404(self, client):
        user = UserFactory()

        client.force_login(user)
        response = client.get(
            "/web/profile/00000000-0000-0000-0000-000000000000/following/"
        )

        assert response.status_code == 404


class TestTopbarProfileLink:
    def test_topbar_links_to_own_profile(self, client):
        """Scenario: Topbar links to own profile."""
        user = UserFactory()

        client.force_login(user)
        response = client.get("/web/")

        content = response.content.decode()
        assert f'href="/web/profile/{user.id}/"' in content
        assert "Profile" in content
        assert 'class="sidebar"' in content

    def test_topbar_has_no_profile_link_for_anonymous(self, client):
        response = client.get("/web/login/")

        content = response.content.decode()
        assert "/web/profile/" not in content
        assert 'class="sidebar"' not in content
