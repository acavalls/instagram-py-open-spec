"""Delete expired stories together with their view records."""

from django.core.management.base import BaseCommand

from apps.posts.services import StoryService


class Command(BaseCommand):
    help = "Delete expired stories and report the number removed."

    def handle(self, *args, **options):
        deleted_count = StoryService.cleanup_expired()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted_count} expired story(ies)")
        )
