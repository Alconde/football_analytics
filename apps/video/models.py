from django.core.exceptions import ValidationError

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
    def clean(self):
        """Validar que el timestamp esté dentro de la duración del vídeo"""
        super().clean()
        if self.video and self.second_mark:
            if self.second_mark > self.video.duration_seconds:
                raise ValidationError({
                    'second_mark': f'El marcador ({self.second_mark}s) excede la duración del vídeo ({self.video.duration_seconds}s)'
                })
            if self.second_mark < 0:
                raise ValidationError({
                    'second_mark': 'El marcador no puede ser negativo'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
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
    def clean(self):
        """Validar rango de inicio y fin del clip"""
        super().clean()
        
        if self.start_second is not None and self.end_second is not None:
            if self.start_second >= self.end_second:
                raise ValidationError({
                    'start_second': 'El inicio debe ser menor que el fin',
                    'end_second': 'El fin debe ser mayor que el inicio'
                })
            
            if self.video and self.video.duration_seconds:
                if self.end_second > self.video.duration_seconds:
                    raise ValidationError({
                        'end_second': f'El fin ({self.end_second}s) excede la duración del vídeo'
                    })
        
        if self.start_second is not None and self.start_second < 0:
            raise ValidationError({'start_second': 'El inicio no puede ser negativo'})
        
        if self.end_second is not None and self.end_second < 0:
            raise ValidationError({'end_second': 'El fin no puede ser negativo'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    class Meta:
        ordering = ["video", "start_second"]

    def __str__(self) -> str:
        return self.title
