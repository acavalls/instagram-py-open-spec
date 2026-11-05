from uuid import UUID

from django.db.models import QuerySet

from apps.posts.models import Post, PostMedia


class PostService:
    """Service for post-related business logic."""

    @staticmethod
    def get_by_id(post_id: UUID) -> Post | None:
        return (
            Post.objects.select_related("owner")
            .prefetch_related("media")
            .filter(id=post_id)
            .first()
        )

    @staticmethod
    def list_for_user(
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> QuerySet[Post]:
        return (
            Post.objects.filter(owner_id=user_id)
            .select_related("owner")
            .prefetch_related("media")
            .order_by("-created_at")[offset : offset + limit]
        )

    @staticmethod
    def exists(post_id: UUID) -> bool:
        return Post.objects.filter(id=post_id).exists()

    @staticmethod
    def is_owner(post_id: UUID, user_id: UUID) -> bool:
        return Post.objects.filter(id=post_id, owner_id=user_id).exists()

    def create(
        self,
        owner_id: UUID,
        caption: str,
        media_files: list[dict] | None = None,
    ) -> Post:
        post = Post.objects.create(owner_id=owner_id, caption=caption)

        if media_files:
            media_objects = [
                PostMedia(
                    post=post,
                    file=media["file"],
                    media_type=media.get("media_type", PostMedia.MediaType.IMAGE),
                    order=media.get("order", idx),
                )
                for idx, media in enumerate(media_files)
            ]
            PostMedia.objects.bulk_create(media_objects)

        return post

    def update_caption(self, post: Post, caption: str) -> Post:
        post.caption = caption
        post.save(update_fields=["caption", "updated_at"])
        return post

    def delete(self, post: Post) -> None:
        post.delete()
