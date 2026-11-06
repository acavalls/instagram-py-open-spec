"""Admin configuration for social models."""

from django.contrib import admin

from apps.social.models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")
    readonly_fields = ("id", "created_at")
    date_hierarchy = "created_at"
