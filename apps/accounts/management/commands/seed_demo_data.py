"""Seed demo data — creates a demo ecosystem for manual validation."""

import random

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.accounts.services import UserService
from apps.accounts.use_cases import RegisterUserInput, RegisterUserUseCase
from apps.posts.services import PostService, StoryService
from apps.posts.use_cases import (
    CreatePostInput,
    CreatePostUseCase,
    CreateStoryInput,
    CreateStoryUseCase,
)
from apps.social.services import FollowService

DEMO_USERS = ["demo_alice", "demo_bob", "demo_carol", "demo_dave", "demo_eve"]

DEMO_FOLLOWS = [
    ("demo_alice", "demo_bob"),
    ("demo_alice", "demo_carol"),
    ("demo_alice", "demo_dave"),
    ("demo_bob", "demo_alice"),
    ("demo_carol", "demo_alice"),
]

DEMO_STORY_OWNERS = ["demo_bob", "demo_carol"]

DEMO_PASSWORD = "demopass123"

GIF_BYTES = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9"
    b"\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02\x4c\x01\x00\x3b"
)

CAPTIONS = [
    "Golden hour vibes",
    "Coffee and mornings",
    "City lights",
    "Weekend escape",
    "Making memories",
]


class Command(BaseCommand):
    help = "Seed demo users, follows and posts with generated placeholders."

    def handle(self, *args, **options):
        if User.objects.filter(username__in=DEMO_USERS).exists():
            self.stdout.write(
                self.style.WARNING("Demo users already exist — skipping seed")
            )
            return

        user_service = UserService()
        users = {}
        for username in DEMO_USERS:
            output = RegisterUserUseCase(user_service=user_service).execute(
                RegisterUserInput(
                    email=f"{username}@example.com",
                    username=username,
                    password=DEMO_PASSWORD,
                )
            )
            if not output.success or output.user_id is None:
                self.stderr.write(
                    self.style.ERROR(f"Failed to create {username}: {output.error}")
                )
                return
            users[username] = user_service.get_by_id(output.user_id)
            self.stdout.write(f"Created user {username}")

        follow_service = FollowService()
        for follower, following in DEMO_FOLLOWS:
            success, error = follow_service.follow(
                users[follower].id, users[following].id
            )
            if not success:
                self.stderr.write(
                    self.style.ERROR(f"Failed follow {follower}->{following}: {error}")
                )
                return
            self.stdout.write(f"Created follow {follower} -> {following}")

        post_service = PostService()
        captions = random.choices(CAPTIONS, k=len(users))
        for idx, (owner, caption) in enumerate(
            zip(users.values(), captions, strict=True)
        ):
            color = random.randint(0, 0xFFFFFF)
            placeholder = SimpleUploadedFile(
                f"seed_{idx}_{color}.jpg", GIF_BYTES, content_type="image/jpeg"
            )
            output = CreatePostUseCase(post_service=post_service).execute(
                CreatePostInput(
                    owner_id=owner.id,
                    caption=caption,
                    media_files=[
                        {"file": placeholder, "media_type": "image", "order": 0}
                    ],
                )
            )
            if not output.success:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed post for {owner.username}: {output.error}"
                    )
                )
                return
            self.stdout.write(f"Created post for {owner.username}")

        story_service = StoryService()
        for owner_name in DEMO_STORY_OWNERS:
            output = CreateStoryUseCase(story_service=story_service).execute(
                CreateStoryInput(owner_id=users[owner_name].id)
            )
            if not output.success:
                self.stderr.write(
                    self.style.ERROR(f"Failed story for {owner_name}: {output.error}")
                )
                return
            self.stdout.write(f"Created story for {owner_name}")

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully"))
