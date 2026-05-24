from django.core.exceptions import ValidationError
from django.db import models

from apps.clubs.models import Competition, Season, Team
from apps.core.managers import MatchManager

class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Programado"
        FINISHED = "finished", "Finalizado"
        POSTPONED = "postponed", "Aplazado"
        CANCELLED = "cancelled", "Cancelado"

    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name="matches",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
    )
    match_date = models.DateTimeField(
        verbose_name="Fecha y hora del partido",
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="home_matches",
        verbose_name="Equipo local",
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="away_matches",
        verbose_name="Equipo visitante",
    )
    home_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Goles local",
    )
    away_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Goles visitante",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name="Estado",
    )
    venue = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Estadio / sede",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    objects = MatchManager()
    class Meta:
        ordering = ["-match_date"]
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(home_team=models.F("away_team")),
                name="matches_home_team_not_equal_away_team",
            ),
        ]
        indexes = [
            models.Index(fields=["match_date"], name="matches_match_date_idx"),
            models.Index(fields=["status"], name="matches_status_idx"),
            models.Index(fields=["season", "match_date"], name="matches_season_date_idx"),
            models.Index(fields=["competition", "match_date"], name="matches_comp_date_idx"),
            models.Index(fields=["home_team"], name="matches_home_team_idx"),
            models.Index(fields=["away_team"], name="matches_away_team_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.home_team} vs {self.away_team} · {self.match_date:%d/%m/%Y %H:%M}"

    def clean(self):
        errors = {}

        if self.home_team and self.away_team and self.home_team == self.away_team:
            errors["away_team"] = "El equipo local y el visitante no pueden ser el mismo."

        if self.status == self.Status.FINISHED:
            if self.home_score is None:
                errors["home_score"] = "Si el partido está finalizado, debes indicar el marcador local."
            if self.away_score is None:
                errors["away_score"] = "Si el partido está finalizado, debes indicar el marcador visitante."

        if self.status in {self.Status.SCHEDULED, self.Status.POSTPONED, self.Status.CANCELLED}:
            if self.home_score is not None or self.away_score is not None:
                errors["status"] = (
                    "Solo los partidos finalizados deberían tener marcador informado."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def is_finished(self) -> bool:
        return self.status == self.Status.FINISHED

    @property
    def display_score(self) -> str:
        if self.home_score is None or self.away_score is None:
            return "-"
        return f"{self.home_score} - {self.away_score}"


class MatchTeamStat(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="team_stats",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="match_stats",
    )
    possession_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Posesión %",
    )
    xg = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="xG",
    )
    shots = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tiros",
    )
    shots_on_target = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tiros a puerta",
    )
    passes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Pases",
    )
    pass_accuracy_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precisión de pase %",
    )
    ppda = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PPDA",
    )
    recoveries = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Recuperaciones",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-match__match_date", "team__name"]
        verbose_name = "Estadística de equipo por partido"
        verbose_name_plural = "Estadísticas de equipo por partido"
        constraints = [
            models.UniqueConstraint(
                fields=["match", "team"],
                name="matches_unique_match_team_stat",
            ),
        ]
        indexes = [
            models.Index(fields=["match"], name="mts_match_idx"),
            models.Index(fields=["team"], name="mts_team_idx"),
            models.Index(fields=["match", "team"], name="mts_match_team_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.match} · {self.team}"

    def clean(self):
        errors = {}

        if self.match_id and self.team_id:
            valid_team_ids = {self.match.home_team_id, self.match.away_team_id}
            if self.team_id not in valid_team_ids:
                errors["team"] = "El equipo debe ser uno de los dos participantes del partido."

        numeric_non_negative_fields = {
            "shots": self.shots,
            "shots_on_target": self.shots_on_target,
            "passes": self.passes,
            "recoveries": self.recoveries,
        }
        for field_name, value in numeric_non_negative_fields.items():
            if value is not None and value < 0:
                errors[field_name] = "Este valor no puede ser negativo."

        if (
            self.shots is not None
            and self.shots_on_target is not None
            and self.shots_on_target > self.shots
        ):
            errors["shots_on_target"] = "Los tiros a puerta no pueden ser mayores que los tiros totales."

        if self.possession_pct is not None and not (0 <= self.possession_pct <= 100):
            errors["possession_pct"] = "La posesión debe estar entre 0 y 100."

        if self.pass_accuracy_pct is not None and not (0 <= self.pass_accuracy_pct <= 100):
            errors["pass_accuracy_pct"] = "La precisión de pase debe estar entre 0 y 100."

        if self.xg is not None and self.xg < 0:
            errors["xg"] = "El xG no puede ser negativo."

        if self.ppda is not None and self.ppda < 0:
            errors["ppda"] = "El PPDA no puede ser negativo."

        if errors:
            raise ValidationError(errors)