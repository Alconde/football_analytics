from django.db import models

from apps.players.models import Player
from apps.matches.models import Match


class WellnessReport(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="wellness_reports")
    report_date = models.DateField()

    fatigue = models.PositiveSmallIntegerField(default=0)      # 0-10
    soreness = models.PositiveSmallIntegerField(default=0)     # 0-10
    stress = models.PositiveSmallIntegerField(default=0)       # 0-10
    sleep_quality = models.PositiveSmallIntegerField(default=0)  # 0-10
    rpe = models.PositiveSmallIntegerField(default=0)          # 0-10

    class Meta:
        unique_together = ("player", "report_date")
        ordering = ["-report_date"]

    def __str__(self) -> str:
        return f"{self.player} - {self.report_date}"


class GPSLoad(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="gps_loads")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="gps_loads", null=True, blank=True)
    session_date = models.DateField()

    total_distance_m = models.PositiveIntegerField(default=0)
    high_speed_distance_m = models.PositiveIntegerField(default=0)
    sprint_count = models.PositiveSmallIntegerField(default=0)
    max_speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    accel_count = models.PositiveSmallIntegerField(default=0)
    decel_count = models.PositiveSmallIntegerField(default=0)
    workload_index = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-session_date"]

    def __str__(self) -> str:
        return f"{self.player} - GPS {self.session_date}"
