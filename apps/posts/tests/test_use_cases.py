import pytest

from apps.accounts.tests.factories import UserFactory
from apps.posts.services import PostService
from apps.posts.tests.factories import PostFactory, make_image
from apps.posts.use_cases import (
    CreatePostInput,
    CreatePostUseCase,
    DeletePostInput,
    DeletePostUseCase,
    GetPostInput,
    GetPostUseCase,
    ListPostsInput,
    ListPostsUseCase,
    UpdatePostInput,
    UpdatePostUseCase,
)

pytestmark = pytest.mark.django_db


class TestCreatePostUseCase:
    def test_successful_creation(self):
        user = UserFactory()
        use_case = CreatePostUseCase(post_service=PostService())

        output = use_case.execute(
            CreatePostInput(
                owner_id=user.id,
                caption="hello",
                media_files=[{"file": make_image(), "media_type": "image", "order": 0}],
            )
        )

        assert output.success
        assert output.post_id is not None
        assert output.error is None


class TestListPostsUseCase:
    def test_lists_own_posts_newest_first(self):
        user = UserFactory()
        other = UserFactory()
        own_posts = [PostFactory(owner=user) for _ in range(2)]
        PostFactory(owner=other)
        use_case = ListPostsUseCase(post_service=PostService())

        output = use_case.execute(ListPostsInput(user_id=user.id))

        assert output.success
        assert [p.id for p in output.posts] == [own_posts[1].id, own_posts[0].id]


class TestGetPostUseCase:
    def test_existing_post_found(self):
        post = PostFactory()
        use_case = GetPostUseCase(post_service=PostService())

        output = use_case.execute(GetPostInput(post_id=post.id))

        assert output.success
        assert output.post is not None

    def test_unknown_post_not_found(self):
        import uuid

        use_case = GetPostUseCase(post_service=PostService())

        output = use_case.execute(GetPostInput(post_id=uuid.uuid4()))

        assert not output.success
        assert output.error == "Post not found"


class TestUpdatePostUseCase:
    def test_owner_updates_caption(self):
        user = UserFactory()
        post = PostFactory(owner=user)
        use_case = UpdatePostUseCase(post_service=PostService())

        output = use_case.execute(
            UpdatePostInput(post_id=post.id, user_id=user.id, caption="new caption")
        )

        assert output.success
        assert output.post_id == post.id

    def test_non_owner_update_rejected(self):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        use_case = UpdatePostUseCase(post_service=PostService())

        output = use_case.execute(
            UpdatePostInput(post_id=post.id, user_id=other.id, caption="hack")
        )

        assert not output.success
        assert output.error == "You can only edit your own posts"

    def test_unknown_post_update_not_found(self):
        import uuid

        user = UserFactory()
        use_case = UpdatePostUseCase(post_service=PostService())

        output = use_case.execute(
            UpdatePostInput(post_id=uuid.uuid4(), user_id=user.id, caption="x")
        )

        assert not output.success
        assert output.error == "Post not found"


class TestDeletePostUseCase:
    def test_owner_deletes_post(self):
        user = UserFactory()
        post = PostFactory(owner=user)
        use_case = DeletePostUseCase(post_service=PostService())

        output = use_case.execute(DeletePostInput(post_id=post.id, user_id=user.id))

        assert output.success
        assert PostService.get_by_id(post.id) is None

    def test_non_owner_deletion_rejected(self):
        owner = UserFactory()
        other = UserFactory()
        post = PostFactory(owner=owner)
        use_case = DeletePostUseCase(post_service=PostService())

        output = use_case.execute(DeletePostInput(post_id=post.id, user_id=other.id))

        assert not output.success
        assert output.error == "You can only delete your own posts"

    def test_unknown_post_deletion_not_found(self):
        import uuid

        user = UserFactory()
        use_case = DeletePostUseCase(post_service=PostService())

        output = use_case.execute(
            DeletePostInput(post_id=uuid.uuid4(), user_id=user.id)
        )

        assert not output.success
        assert output.error == "Post not found"


class TestUpdatePostCaptionLimit:
    def test_caption_over_2200_chars_rejected(self):
        """Scenario: Caption length limit."""
        user = UserFactory()
        post = PostFactory(owner=user)
        use_case = UpdatePostUseCase(post_service=PostService())

        output = use_case.execute(
            UpdatePostInput(post_id=post.id, user_id=user.id, caption="x" * 2201)
        )

        assert output.success is False
        assert output.error == "Caption must be 2200 characters or fewer"
        post.refresh_from_db()
        assert post.caption != "x" * 2201

    def test_caption_exactly_2200_chars_accepted(self):
        user = UserFactory()
        post = PostFactory(owner=user)
        use_case = UpdatePostUseCase(post_service=PostService())

        output = use_case.execute(
            UpdatePostInput(post_id=post.id, user_id=user.id, caption="x" * 2200)
        )

        assert output.success is True
        post.refresh_from_db()
        assert post.caption == "x" * 2200
