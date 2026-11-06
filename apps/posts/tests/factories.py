from datetime import timedelta

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.posts.models import Post, PostMedia, Story, StoryView

GIF_BYTES = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9"
    b"\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02\x4c\x01\x00\x3b"
)


def make_image(name: str = "test_image.jpg") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, GIF_BYTES, content_type="image/jpeg")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    owner = factory.SubFactory(UserFactory)
    caption = factory.Faker("sentence")


class PostMediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostMedia

    post = factory.SubFactory(PostFactory)
    file = factory.LazyAttribute(lambda _: make_image())
    media_type = PostMedia.MediaType.IMAGE
    order = 0


class StoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Story

    owner = factory.SubFactory(UserFactory)
    file = factory.LazyAttribute(lambda _: make_image("test_story.jpg"))
    media_type = Story.MediaType.IMAGE
    expires_at = factory.LazyAttribute(
        lambda _: timezone.now() + timedelta(hours=24)
    )


class StoryViewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StoryView

    story = factory.SubFactory(StoryFactory)
    viewer = factory.SubFactory(UserFactory)
