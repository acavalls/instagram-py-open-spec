import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import Post
from apps.posts.tests.factories import PostFactory, PostMediaFactory, make_image

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_post_persisted_with_media(self):
        user = UserFactory()
        post = Post.objects.create(owner=user, caption="hello world")
        PostMediaFactory(post=post, file=make_image("first.jpg"), order=0)
        PostMediaFactory(post=post, file=make_image("second.jpg"), order=1)

        stored = Post.objects.filter(id=post.id).select_related("owner").first()

        assert stored is not None
        assert stored.owner_id == user.id
        assert stored.caption == "hello world"
        assert stored.created_at is not None
        assert stored.updated_at is not None
        media = list(stored.media.all())
        assert len(media) == 2
        assert media[0].order == 0
        assert media[1].order == 1
        assert media[0].media_type == "image"

    def test_ownership_rules(self):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)

        can_edit, edit_error = post.can_edit(owner.id)
        assert can_edit
        assert edit_error == ""

        can_edit, edit_error = post.can_edit(other.id)
        assert not can_edit
        assert edit_error == "You can only edit your own posts"

        can_delete, delete_error = post.can_delete(other.id)
        assert not can_delete
        assert delete_error == "You can only delete your own posts"

    def test_deleting_post_cascades_media(self):
        from apps.posts.models import PostMedia

        post = PostFactory()
        PostMediaFactory(post=post)
        post_id = post.id

        post.delete()

        assert not Post.objects.filter(id=post_id).exists()
        assert not PostMedia.objects.filter(post_id=post_id).exists()


class TestPostMediaStorage:
    def test_media_stored_under_dated_path(self):
        """Scenario: Media stored under dated path."""
        user = UserFactory()
        post = PostFactory(owner=user)
        media = PostMediaFactory(post=post, file=make_image("dated.jpg"))

        assert media.file.name.startswith("post_examples/")
        assert "/20" in media.file.name  # <year>/<month>/<day> segments present

        url = media.file.url

        assert url.startswith("/media/post_examples/")
