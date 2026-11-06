"""Tests for follow/unfollow use cases.

Scenarios: Self-follow rejected, Duplicate follow rejected, Web follow
failure shows the cause (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.social.services import FollowService
from apps.social.tests.factories import FollowFactory
from apps.social.use_cases import (
    FollowUserInput,
    FollowUserUseCase,
    UnfollowUserInput,
    UnfollowUserUseCase,
)

pytestmark = pytest.mark.django_db


class TestFollowUserUseCase:
    def test_successful_follow(self):
        follower = UserFactory()
        following = UserFactory()
        use_case = FollowUserUseCase(follow_service=FollowService())

        output = use_case.execute(
            FollowUserInput(follower_id=follower.id, following_id=following.id)
        )

        assert output.success is True
        assert output.error is None

    def test_self_follow_returns_error(self):
        user = UserFactory()
        use_case = FollowUserUseCase(follow_service=FollowService())

        output = use_case.execute(
            FollowUserInput(follower_id=user.id, following_id=user.id)
        )

        assert output.success is False
        assert output.error == "You cannot follow yourself"

    def test_duplicate_follow_returns_error(self):
        follower = UserFactory()
        following = UserFactory()
        FollowFactory(follower=follower, following=following)
        use_case = FollowUserUseCase(follow_service=FollowService())

        output = use_case.execute(
            FollowUserInput(follower_id=follower.id, following_id=following.id)
        )

        assert output.success is False
        assert output.error == "Already following this user"


class TestUnfollowUserUseCase:
    def test_successful_unfollow(self):
        follower = UserFactory()
        following = UserFactory()
        FollowFactory(follower=follower, following=following)
        use_case = UnfollowUserUseCase(follow_service=FollowService())

        output = use_case.execute(
            UnfollowUserInput(follower_id=follower.id, following_id=following.id)
        )

        assert output.success is True
        assert output.error is None

    def test_unfollow_unknown_relationship_returns_error(self):
        follower = UserFactory()
        following = UserFactory()
        use_case = UnfollowUserUseCase(follow_service=FollowService())

        output = use_case.execute(
            UnfollowUserInput(follower_id=follower.id, following_id=following.id)
        )

        assert output.success is False
        assert output.error == "Follow relationship not found"
