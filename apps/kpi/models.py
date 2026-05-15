from django.db import models

from apps.matches.models import Match
from apps.clubs.models import Team
from apps.players.models import Player


class KPIType(models.Model):
    code = models.CharField(max_length=40, unique=True)  # xg, ppda, duels_won_pct...
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, blank=True)  # %, m, count, ratio

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class MatchKPI(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="kpis")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_kpis")
    kpi_type = models.ForeignKey(KPIType, on_delete=models.PROTECT, related_name="match_values")
    value = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        unique_together = ("match", "team", "kpi_type")
        ordering = ["-match__match_date"]

    def __str__(self) -> str:
        return f"{self.kpi_type.code}={self.value} ({self.team})"


class PlayerKPI(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="player_kpis")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="match_kpis")
    kpi_type = models.ForeignKey(KPIType, on_delete=models.PROTECT, related_name="player_values")
    value = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        unique_together = ("match", "player", "kpi_type")
        ordering = ["-match__match_date"]

    def __str__(self) -> str:
        return f"{self.player} {self.kpi_type.code}={self.value}"