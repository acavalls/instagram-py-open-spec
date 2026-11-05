import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.tests.factories import PostFactory, PostMediaFactory, make_image

pytestmark = pytest.mark.django_db


class TestPostListCreateView:
    def test_successful_api_creation(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/posts/",
            {"caption": "my first post", "media": [make_image("one.jpg")]},
            format="multipart",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["caption"] == "my first post"
        assert data["owner_username"] == user.username
        assert data["media_count"] == 1
        assert data["media"][0]["order"] == 0
        assert data["media"][0]["media_type"] == "image"

    def test_api_creation_without_media_is_valid(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/posts/", {"caption": "text only"}, format="multipart"
        )

        assert response.status_code == 201
        assert response.json()["media_count"] == 0

    def test_api_creation_with_too_many_media_files(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/posts/",
            {
                "caption": "too many",
                "media": [make_image(f"f{i}.jpg") for i in range(11)],
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert "media" in response.json()

    def test_caption_length_limit(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/posts/", {"caption": "x" * 2201}, format="multipart"
        )

        assert response.status_code == 400
        assert "caption" in response.json()

    def test_caption_length_limit_on_update(self, api_client):
        user = UserFactory()
        post = PostFactory(owner=user)
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            f"/api/posts/{post.id}/",
            {"caption": "x" * 2201},
            format="json",
        )

        assert response.status_code == 400
        assert "caption" in response.json()
        post.refresh_from_db()
        assert post.caption != "x" * 2201

    def test_api_list_of_own_posts(self, api_client):
        user = UserFactory()
        posts = [PostFactory(owner=user) for _ in range(2)]
        PostMediaFactory(post=posts[0], file=make_image("p0.jpg"))
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/posts/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == str(posts[1].id)
        assert data[1]["id"] == str(posts[0].id)
        assert data[1]["first_image_url"] is not None

    def test_no_cross_user_listing(self, api_client):
        user = UserFactory()
        other = UserFactory()
        PostFactory(owner=other)
        own = PostFactory(owner=user)
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/posts/")

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(own.id)

    def test_pagination_window(self, api_client):
        user = UserFactory()
        posts = [PostFactory(owner=user) for _ in range(3)]
        api_client.force_authenticate(user=user)

        page1 = api_client.get("/api/posts/?limit=2&offset=0").json()
        page2 = api_client.get("/api/posts/?limit=2&offset=2").json()

        assert [p["id"] for p in page1] == [str(posts[2].id), str(posts[1].id)]
        assert [p["id"] for p in page2] == [str(posts[0].id)]


class TestPostDetailView:
    def test_existing_post_detail(self, api_client):
        user = UserFactory()
        post = PostFactory(owner=user, caption="detail")
        PostMediaFactory(post=post, file=make_image("d.jpg"))
        api_client.force_authenticate(user=user)

        response = api_client.get(f"/api/posts/{post.id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["caption"] == "detail"
        assert data["media_count"] == 1

    def test_unknown_post_detail(self, api_client):
        import uuid

        user = UserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.get(f"/api/posts/{uuid.uuid4()}/")

        assert response.status_code == 404
        assert response.json()["error"] == "Post not found"

    def test_owner_updates_caption_via_api(self, api_client):
        user = UserFactory()
        post = PostFactory(owner=user, caption="before")
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            f"/api/posts/{post.id}/",
            {"caption": "after"},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["caption"] == "after"
        post.refresh_from_db()
        assert post.caption == "after"

    def test_non_owner_update_rejected(self, api_client):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        api_client.force_authenticate(user=other)

        response = api_client.patch(
            f"/api/posts/{post.id}/",
            {"caption": "hack"},
            format="json",
        )

        assert response.status_code == 403
        assert response.json()["error"] == "You can only edit your own posts"

    def test_owner_deletes_post_via_api(self, api_client):
        user = UserFactory()
        post = PostFactory(owner=user)
        PostMediaFactory(post=post)
        api_client.force_authenticate(user=user)

        response = api_client.delete(f"/api/posts/{post.id}/")

        assert response.status_code == 204
        assert not user.posts.filter(id=post.id).exists()

    def test_non_owner_deletion_rejected(self, api_client):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        api_client.force_authenticate(user=other)

        response = api_client.delete(f"/api/posts/{post.id}/")

        assert response.status_code == 403
        assert response.json()["error"] == "You can only delete your own posts"
