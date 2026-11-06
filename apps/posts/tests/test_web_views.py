from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import Post
from apps.posts.tests.factories import PostFactory
from apps.social.tests.factories import FollowFactory

pytestmark = pytest.mark.django_db


class TestCreateRandomPostView:
    def test_successful_web_creation(self, client):
        user = UserFactory()
        client.force_login(user)

        response = client.post("/web/posts/create/")

        assert response.status_code == 302
        assert response.url == "/web/"
        follow = client.get(response.url)
        assert b"Post created!" in follow.content
        assert user.posts.count() == 1
        assert list(user.posts.first().media.all())


class TestIndexView:
    def test_personal_feed_on_the_home_page(self, client):
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        PostFactory(owner=followed, caption="followed post")
        PostFactory(owner=user, caption="my own post")
        client.force_login(user)

        response = client.get("/web/")

        assert response.status_code == 200
        content = response.content
        assert b"followed post" in content
        assert b"my own post" not in content

    def test_pagination_window(self, client):
        user = UserFactory()
        followed = UserFactory()
        FollowFactory(follower=user, following=followed)
        posts = [PostFactory(owner=followed) for _ in range(13)]
        now = timezone.now()
        for idx, post in enumerate(posts):
            Post.objects.filter(pk=post.pk).update(
                created_at=now - timedelta(minutes=len(posts) - idx)
            )
        client.force_login(user)

        page1 = client.get("/web/")
        page2 = client.get("/web/?page=2", HTTP_HX_REQUEST="true")

        assert posts[12].caption.encode() in page1.content
        assert posts[0].caption.encode() in page2.content
        assert b"infinite-scroll-sentinel" in page1.content
        assert b"No more posts" in page2.content
        assert b"<!DOCTYPE html>" not in page2.content


class TestEditFlow:
    def test_inline_web_edit(self, client):
        user = UserFactory()
        post = PostFactory(owner=user, caption="before")
        client.force_login(user)

        form = client.get(f"/web/posts/{post.id}/edit-form/")
        assert form.status_code == 200
        assert b'name="caption"' in form.content

        response = client.post(
            f"/web/posts/{post.id}/submit-edit/", {"caption": "after"}
        )

        assert response.status_code == 200
        assert b"Post updated!" in response.content
        assert b"after" in response.content
        post.refresh_from_db()
        assert post.caption == "after"

    def test_cancel_inline_edit(self, client):
        user = UserFactory()
        post = PostFactory(owner=user, caption="kept")
        client.force_login(user)

        response = client.get(f"/web/posts/{post.id}/cancel-edit/")

        assert response.status_code == 200
        assert b"hidden" in response.content
        post.refresh_from_db()
        assert post.caption == "kept"

    def test_edit_form_rejected_for_non_owner(self, client):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        client.force_login(other)

        response = client.get(f"/web/posts/{post.id}/edit-form/")

        assert response.status_code == 404


class TestDeletePostView:
    def test_web_deletion_removes_the_card(self, client):
        user = UserFactory()
        post = PostFactory(owner=user)
        client.force_login(user)

        response = client.post(f"/web/posts/{post.id}/delete/")

        assert response.status_code == 200
        assert b"Post deleted!" in response.content
        assert b"hidden" in response.content
        assert not user.posts.filter(id=post.id).exists()

    def test_web_deletion_rejected_for_non_owner(self, client):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        client.force_login(other)

        response = client.post(f"/web/posts/{post.id}/delete/")

        assert response.status_code == 200
        assert b"You can only delete your own posts" in response.content
        assert owner.posts.filter(id=post.id).exists()


class TestEditCaptionLimit:
    def test_web_edit_with_oversized_caption_rejected(self, client):
        """Scenario: Caption length limit."""
        user = UserFactory()
        post = PostFactory(owner=user, caption="original")
        client.force_login(user)

        response = client.post(
            f"/web/posts/{post.id}/submit-edit/", {"caption": "x" * 2201}
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Caption must be 2200 characters or fewer" in content
        post.refresh_from_db()
        assert post.caption == "original"
