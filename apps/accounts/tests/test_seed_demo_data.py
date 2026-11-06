"""Tests for the seed_demo_data management command."""

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.posts.models import Post
from apps.social.models import Follow

pytestmark = pytest.mark.django_db


class TestSeedDemoData:
    def test_seeds_users_follows_and_posts(self):
        call_command("seed_demo_data", verbosity=0)

        assert User.objects.filter(username__startswith="demo_").count() == 5
        assert Follow.objects.count() == 5
        assert Post.objects.count() == 5

    def test_is_idempotent_skips_when_demo_users_exist(self):
        call_command("seed_demo_data", verbosity=0)
        call_command("seed_demo_data", verbosity=0)

        assert User.objects.filter(username__startswith="demo_").count() == 5
        assert Post.objects.count() == 5
