from rest_framework import serializers

from apps.posts.models import Post, PostMedia


class PostMediaReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["id", "file", "media_type", "order"]
        read_only_fields = fields


class PostReadSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    media = PostMediaReadSerializer(many=True, read_only=True)
    media_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "owner_username",
            "caption",
            "media",
            "media_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_media_count(self, obj: Post) -> int:
        return obj.media.count()  # type: ignore[attr-defined]


class PostListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    media_count = serializers.SerializerMethodField()
    first_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "owner_username",
            "caption",
            "media_count",
            "first_image_url",
            "created_at",
        ]
        read_only_fields = fields

    def get_media_count(self, obj: Post) -> int:
        return obj.media.count()  # type: ignore[attr-defined]

    def get_first_image_url(self, obj: Post) -> str | None:
        first_media = obj.media.filter(order=0).first()  # type: ignore[attr-defined]
        if first_media:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_media.file.url)
            return first_media.file.url
        return None


class PostCreateSerializer(serializers.Serializer):
    caption = serializers.CharField(
        max_length=2200,
        required=False,
        allow_blank=True,
        default="",
    )
    media = serializers.ListField(
        child=serializers.ImageField(),
        max_length=10,
        required=False,
        default=list,
    )


class PostUpdateSerializer(serializers.Serializer):
    caption = serializers.CharField(max_length=2200, required=True)
