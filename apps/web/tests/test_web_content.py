"""Tests for web content behaviors (infinite scroll, card, profile, empty).

Scenarios: Feed loads more posts on scroll, Profile grid loads more posts
on scroll, Card header shows owner avatar and username link, Card actions
row renders placeholders, Missing media renders the placeholder icon,
Profile header shows avatar, stats and tabs, Following stat opens the modal,
Grid item shows overlay (spec deltas: posts, social, web-ui)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import Post
from apps.posts.tests.factories import PostFactory
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


def _seed_posts(owner, count):
    posts = [PostFactory(owner=owner) for _ in range(count)]
    now = timezone.now()
    for idx, post in enumerate(posts):
        Post.objects.filter(pk=post.pk).update(
            created_at=now - timedelta(minutes=count - idx)
        )
    return posts


class TestFeedInfiniteScroll:
    def test_feed_loads_more_posts_on_scroll(self, client):
        """Scenario: Feed loads more posts on scroll."""
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        _seed_posts(followed, 13)
        client.force_login(user)

        page1 = client.get("/web/")
        partial = client.get("/web/?page=2", HTTP_HX_REQUEST="true")

        assert partial.status_code == 200
        content = partial.content.decode()
        assert 'class="post-card"' in content
        assert "infinite-scroll-end" in content
        assert "<!DOCTYPE html>" not in content
        assert b"infinite-scroll-sentinel" in page1.content

    def test_feed_sentinel_targets_next_page(self, client):
        """Scenario: Feed loads more posts on scroll."""
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        _seed_posts(followed, 13)
        client.force_login(user)

        page1 = client.get("/web/")

        content = page1.content.decode()
        assert 'hx-get="/web/?page=2"' in content
        assert 'hx-trigger="revealed"' in content
        assert 'hx-target="#feed-posts"' in content


class TestProfileInfiniteScroll:
    def test_profile_grid_loads_more_posts_on_scroll(self, client):
        """Scenario: Profile grid loads more posts on scroll."""
        user = UserFactory()
        _seed_posts(user, 13)
        client.force_login(user)

        page1 = client.get(f"/web/profile/{user.id}/")
        partial = client.get(f"/web/profile/{user.id}/?page=2", HTTP_HX_REQUEST="true")

        assert partial.status_code == 200
        content = partial.content.decode()
        assert "profile-grid__item-wrapper" in content
        assert "infinite-scroll-end" in content
        assert "<!DOCTYPE html>" not in content
        assert b"infinite-scroll-sentinel" in page1.content


class TestPostCardAnatomy:
    def test_card_header_shows_owner_avatar_and_username_link(self, client):
        """Scenario: Card header shows owner avatar and username link."""
        user = UserFactory()
        followed = UserFactory(username="cardowner")
        FollowFactory(follower=user, following=followed)
        PostFactory(owner=followed)
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        header = content.split('class="post-card__header"', 1)[1].split("</header>")[0]
        assert "post-card__avatar" in header
        assert f'href="/web/profile/{followed.id}/"' in header
        assert "cardowner" in header

    def test_card_actions_row_renders_placeholders(self, client):
        """Scenario: Card actions row renders placeholders."""
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        PostFactory(owner=followed)
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        actions = content.split('class="post-card__actions"', 1)[1]
        for label in ("Like", "Comment", "Share", "Save"):
            assert f'aria-label="{label}"' in actions
        # Placeholder buttons have no hx-post / href behavior
        assert "hx-post" not in actions.split("</div>")[0]

    def test_missing_media_renders_the_placeholder_icon(self, client):
        """Scenario: Missing media renders the placeholder icon."""
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        PostFactory(owner=followed, caption="medialess")
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        card = content.split('class="post-card__media"', 1)[1]
        assert "bi-image" in card.split("</div>")[0]


class TestProfilePageStructure:
    def test_profile_header_shows_avatar_stats_and_tabs(self, client):
        """Scenario: Profile header shows avatar, stats and tabs."""
        user = UserFactory()
        client.force_login(user)

        response = client.get(f"/web/profile/{user.id}/")

        content = response.content.decode()
        assert "profile-header__avatar" in content
        assert "profile-header__stats" in content
        assert "POSTS" in content
        assert "SAVED" in content
        assert "TAGGED" in content
        assert "profile-tab--active" in content

    def test_following_stat_opens_the_modal(self, client):
        """Scenario: Following stat opens the modal."""
        user = UserFactory()
        client.force_login(user)

        response = client.get(f"/web/profile/{user.id}/")

        content = response.content.decode()
        stats = content.split('class="profile-header__stats"', 1)[1]
        assert f'href="/web/profile/{user.id}/following/"' in stats
        assert 'hx-target="#modal-container"' in stats

    def test_grid_item_shows_overlay(self, client):
        """Scenario: Grid item shows overlay."""
        user = UserFactory()
        PostFactory(owner=user)
        client.force_login(user)

        response = client.get(f"/web/profile/{user.id}/")

        content = response.content.decode()
        assert "profile-grid__overlay" in content
        assert "bi-heart-fill" in content
