from django.db import models

from apps.matches.models import Match
from apps.tactical.models import TacticalPhaseObservation


class VideoAsset(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="videos/matches/")
    duration_seconds = models.PositiveIntegerField(default=0)
    provider = models.CharField(max_length=80, blank=True)  # Hudl, Wyscout, etc.
    external_url = models.URLField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.title


class VideoTag(models.Model):
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name="tags")
    label = models.CharField(max_length=120)  # Presión alta, salida 3+1...
    second_mark = models.PositiveIntegerField()  # segundo exacto en el video
    tactical_phase = models.ForeignKey(
        TacticalPhaseObservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_tags",
    )
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["video", "second_mark"]

    def __str__(self) -> str:
        return f"{self.label} ({self.second_mark}s)"


class VideoClip(models.Model):
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name="clips")
    title = models.CharField(max_length=200)
    start_second = models.PositiveIntegerField()
    end_second = models.PositiveIntegerField()
    export_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["video", "start_second"]

    def __str__(self) -> str:
        return self.title
