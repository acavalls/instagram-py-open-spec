"""Tests for feed and suggestions use cases.

Scenarios: Feed shows followed users' posts, Suggestions exclude followed
users and self, Suggestions limited to newest accounts (spec delta: social)."""

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.tests.factories import PostFactory
from apps.social.services import FeedService
from apps.social.tests.factories import FollowFactory
from apps.social.use_cases import (
    GetUserSuggestionsInput,
    GetUserSuggestionsUseCase,
    ListFeedInput,
    ListFeedUseCase,
)

pytestmark = pytest.mark.django_db


class TestListFeedUseCase:
    def test_lists_followed_users_posts(self):
        user = UserFactory()
        followed = UserFactory()
        stranger = UserFactory()
        FollowFactory(follower=user, following=followed)
        post = PostFactory(owner=followed)
        PostFactory(owner=stranger)

        use_case = ListFeedUseCase(feed_service=FeedService())
        output = use_case.execute(ListFeedInput(user_id=user.id))

        assert output.success is True
        assert output.error is None
        assert [p.id for p in output.posts or []] == [post.id]

    def test_empty_feed_returns_empty_list(self):
        user = UserFactory()
        use_case = ListFeedUseCase(feed_service=FeedService())

        output = use_case.execute(ListFeedInput(user_id=user.id))

        assert output.success is True
        assert output.posts == []


class TestGetUserSuggestionsUseCase:
    def test_suggestions_exclude_self_and_followed(self):
        user = UserFactory()
        followed = UserFactory()
        candidate = UserFactory()
        FollowFactory(follower=user, following=followed)

        use_case = GetUserSuggestionsUseCase(feed_service=FeedService())
        output = use_case.execute(GetUserSuggestionsInput(user_id=user.id))

        assert output.success is True
        users = output.users or []
        assert candidate in users
        assert user not in users
        assert followed not in users

    def test_suggestions_capped_at_limit(self):
        user = UserFactory()
        for i in range(8):
            UserFactory(username=f"candidate{i}")

        use_case = GetUserSuggestionsUseCase(feed_service=FeedService())
        output = use_case.execute(GetUserSuggestionsInput(user_id=user.id, limit=5))

        assert len(output.users or []) == 5
