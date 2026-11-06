"""Tests for FollowService — follow relationship domain logic.

Scenarios: Follow persisted, Self-follow rejected, Duplicate follow rejected
(spec delta: social)."""

from uuid import uuid4

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.social.models import Follow
from apps.social.services import FollowService
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def follow_service():
    return FollowService()


class TestFollow:
    def test_follow_creates_relationship_with_uuid_and_timestamp(self, follow_service):
        """Scenario: Follow persisted."""
        follower = UserFactory()
        following = UserFactory()

        success, error = follow_service.follow(follower.id, following.id)

        assert success is True
        assert error == ""
        follow = Follow.objects.get(follower=follower, following=following)
        assert isinstance(follow.id, type(follow.id))
        assert follow.id.version == 4
        assert follow.created_at is not None

    def test_follow_self_rejected(self, follow_service):
        """Scenario: Self-follow rejected."""
        user = UserFactory()

        success, error = follow_service.follow(user.id, user.id)

        assert success is False
        assert error == "You cannot follow yourself"
        assert not Follow.objects.exists()

    def test_follow_duplicate_rejected(self, follow_service):
        """Scenario: Duplicate follow rejected."""
        follower = UserFactory()
        following = UserFactory()
        FollowFactory(follower=follower, following=following)

        success, error = follow_service.follow(follower.id, following.id)

        assert success is False
        assert error == "Already following this user"
        remaining = Follow.objects.filter(follower=follower, following=following)
        assert remaining.count() == 1


class TestUnfollow:
    def test_unfollow_removes_relationship(self, follow_service):
        follower = UserFactory()
        following = UserFactory()
        FollowFactory(follower=follower, following=following)

        success, error = follow_service.unfollow(follower.id, following.id)

        assert success is True
        assert error == ""
        assert not Follow.objects.filter(
            follower=follower, following=following
        ).exists()

    def test_unfollow_unknown_relationship_rejected(self, follow_service):
        follower = UserFactory()
        following = UserFactory()

        success, error = follow_service.unfollow(follower.id, following.id)

        assert success is False
        assert error == "Follow relationship not found"


class TestFollowQueries:
    def test_is_following_true_and_false(self, follow_service):
        follower = UserFactory()
        following = UserFactory()
        other = UserFactory()

        FollowFactory(follower=follower, following=following)

        assert follow_service.is_following(follower.id, following.id) is True
        assert follow_service.is_following(follower.id, other.id) is False
        assert follow_service.is_following(uuid4(), following.id) is False

    def test_get_following_ordered_by_username(self, follow_service):
        user = UserFactory(username="mainuser")
        followed_a = UserFactory(username="alice")
        followed_b = UserFactory(username="bob")
        FollowFactory(follower=user, following=followed_b)
        FollowFactory(follower=user, following=followed_a)

        following = list(follow_service.get_following(user.id))

        assert [u.username for u in following] == ["alice", "bob"]

    def test_get_followers_ordered_by_username(self, follow_service):
        user = UserFactory(username="mainuser")
        follower_a = UserFactory(username="alice")
        follower_b = UserFactory(username="bob")
        FollowFactory(follower=follower_b, following=user)
        FollowFactory(follower=follower_a, following=user)

        followers = list(follow_service.get_followers(user.id))

        assert [u.username for u in followers] == ["alice", "bob"]
