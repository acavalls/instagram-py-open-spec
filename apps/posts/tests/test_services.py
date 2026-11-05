import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.services import PostService
from apps.posts.tests.factories import PostFactory, PostMediaFactory, make_image

pytestmark = pytest.mark.django_db


class TestPostService:
    def test_get_by_id_returns_post_with_owner_and_media(self):
        post = PostFactory()
        PostMediaFactory(post=post, order=0)

        found = PostService.get_by_id(post.id)

        assert found is not None
        assert found.owner.username
        assert list(found.media.all())

    def test_get_by_id_unknown_returns_none(self):
        import uuid

        assert PostService.get_by_id(uuid.uuid4()) is None

    def test_list_for_user_orders_newest_first_and_paginates(self):
        user = UserFactory()
        posts = [PostFactory(owner=user) for _ in range(3)]

        page = list(PostService.list_for_user(user.id, limit=2, offset=0))

        assert len(page) == 2
        assert page[0].id == posts[2].id
        assert page[1].id == posts[1].id

        second_page = list(PostService.list_for_user(user.id, limit=2, offset=2))
        assert [p.id for p in second_page] == [posts[0].id]

    def test_list_for_user_returns_only_own_posts(self):
        user = UserFactory()
        other = UserFactory()
        PostFactory(owner=user)
        PostFactory(owner=other)

        own = list(PostService.list_for_user(user.id))

        assert len(own) == 1
        assert own[0].owner_id == user.id

    def test_create_with_media_bulk_creates_media(self):
        user = UserFactory()

        post = PostService().create(
            owner_id=user.id,
            caption="with media",
            media_files=[
                {"file": make_image("a.jpg"), "media_type": "image", "order": 0},
                {"file": make_image("b.jpg"), "media_type": "image", "order": 1},
            ],
        )

        media = list(post.media.all())
        assert len(media) == 2
        assert media[0].order == 0
        assert media[1].order == 1

    def test_create_without_media_is_valid(self):
        user = UserFactory()

        post = PostService().create(owner_id=user.id, caption="text only")

        assert post.caption == "text only"
        assert post.media.count() == 0

    def test_update_caption_updates_timestamp(self):
        post = PostFactory(caption="before")

        updated = PostService().update_caption(post, "after")

        assert updated.caption == "after"

    def test_delete_removes_post_and_media(self):
        post = PostFactory()
        PostMediaFactory(post=post)

        PostService().delete(post)

        assert PostService.get_by_id(post.id) is None

    def test_is_owner(self):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)

        assert PostService.is_owner(post.id, owner.id)
        assert not PostService.is_owner(post.id, other.id)
