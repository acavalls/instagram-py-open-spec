from django.contrib import admin

from apps.posts.models import Post, PostMedia


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1
    fields = ("file", "media_type", "order")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "caption", "get_media_count", "created_at")
    list_filter = ("created_at", "owner")
    search_fields = ("caption", "owner__username")
    readonly_fields = ("id", "created_at", "updated_at", "get_media_count")
    inlines = [PostMediaInline]

    @admin.display(description="Media Count")
    def get_media_count(self, obj: Post) -> int:
        return obj.media.count()  # type: ignore[attr-defined]


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "media_type", "order")
    list_filter = ("media_type",)
