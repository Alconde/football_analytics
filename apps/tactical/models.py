from django.db import models
from django.conf import settings

from apps.matches.models import Match
from apps.clubs.models import Team


class TacticalReport(models.Model):
    class TeamFocus(models.TextChoices):
        OWN = "own", "Juego propio"
        OPPONENT = "opponent", "Rival"

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="tactical_reports")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tactical_reports")
    team_focus = models.CharField(max_length=10, choices=TeamFocus.choices, default=TeamFocus.OWN)

    system_used = models.CharField(max_length=20, blank=True)  # 4-3-3, 3-4-2-1...
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    recurring_errors = models.TextField(blank=True)
    coach_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="tactical_reports"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Informe táctico {self.team} - {self.match}"


class TacticalPhaseObservation(models.Model):
    class Phase(models.TextChoices):
        BUILD_UP = "build_up", "Salida de balón"
        ATTACK = "attack", "Ataque posicional"
        DEFENSE = "defense", "Organización defensiva"
        OFF_TRANSITION = "off_transition", "Transición ofensiva"
        DEF_TRANSITION = "def_transition", "Transición defensiva"
        SET_PIECE = "set_piece", "Balón parado"
        PRESSING = "pressing", "Presión"

    report = models.ForeignKey(TacticalReport, on_delete=models.CASCADE, related_name="phase_observations")
    phase = models.CharField(max_length=20, choices=Phase.choices)
    minute_start = models.PositiveSmallIntegerField(null=True, blank=True)
    minute_end = models.PositiveSmallIntegerField(null=True, blank=True)
    pattern_detected = models.CharField(max_length=200)
    effectiveness_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["report", "phase", "minute_start"]

    def __str__(self) -> str:
        return f"{self.get_phase_display()} - {self.pattern_detected}"
