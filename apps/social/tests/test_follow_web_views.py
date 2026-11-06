"""Tests for HTMX follow/unfollow web views.

Scenarios: Web follow via HTMX, Web unfollow via HTMX, Web follow failure
shows the cause (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.social.services import FollowService
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestFollowView:
    def test_follow_via_htmx_shows_success_toast_and_new_state(self, client):
        """Scenario: Web follow via HTMX."""
        user = UserFactory()
        target = UserFactory()

        client.force_login(user)
        response = client.post(f"/web/follow/{target.id}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Followed successfully" in content
        assert "follow-btn--unfollow" in content
        assert "Following</button>" in content
        assert FollowService.is_following(user.id, target.id)

    def test_follow_failure_keeps_state_and_shows_error_toast(self, client):
        """Scenario: Web follow failure shows the cause."""
        user = UserFactory()
        target = UserFactory()
        FollowFactory(follower=user, following=target)

        client.force_login(user)
        response = client.post(f"/web/follow/{target.id}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Already following this user" in content
        assert "follow-btn--follow" in content
        assert "Followed successfully" not in content

    def test_follow_requires_login(self, client):
        target = UserFactory()

        response = client.post(f"/web/follow/{target.id}/")

        assert response.status_code == 302
        assert "/web/login/" in response.url


class TestUnfollowView:
    def test_unfollow_via_htmx_shows_success_toast_and_new_state(self, client):
        """Scenario: Web unfollow via HTMX."""
        user = UserFactory()
        target = UserFactory()
        FollowFactory(follower=user, following=target)

        client.force_login(user)
        response = client.post(f"/web/unfollow/{target.id}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Unfollowed successfully" in content
        assert "follow-btn--follow" in content
        assert not FollowService.is_following(user.id, target.id)

    def test_unfollow_failure_keeps_state_and_shows_error_toast(self, client):
        """Scenario: Web follow failure shows the cause."""
        user = UserFactory()
        target = UserFactory()

        client.force_login(user)
        response = client.post(f"/web/unfollow/{target.id}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Follow relationship not found" in content
        assert "follow-btn--unfollow" in content
        assert "Unfollowed successfully" not in content
