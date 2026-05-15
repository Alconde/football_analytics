from django.contrib import admin
from .models import VideoAsset, VideoTag, VideoClip


@admin.register(VideoAsset)
class VideoAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "match", "provider", "duration_seconds", "uploaded_at")
    list_filter = ("provider", "uploaded_at")
    search_fields = ("title", "provider", "match__home_team__name", "match__away_team__name")


@admin.register(VideoTag)
class VideoTagAdmin(admin.ModelAdmin):
    list_display = ("video", "label", "second_mark", "tactical_phase")
    list_filter = ("label",)
    search_fields = ("label", "note")


@admin.register(VideoClip)
class VideoClipAdmin(admin.ModelAdmin):
    list_display = ("video", "title", "start_second", "end_second", "export_path")
    search_fields = ("title", "video__title")
