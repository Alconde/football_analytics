from django.db import models
from django.conf import settings

from apps.clubs.models import Team, Season, Competition


class Player(models.Model):
    class Position(models.TextChoices):
        GK = "GK", "Portero"
        CB = "CB", "Central"
        FB = "FB", "Lateral"
        DM = "DM", "Mediocentro defensivo"
        CM = "CM", "Mediocentro"
        AM = "AM", "Mediapunta"
        WG = "WG", "Extremo"
        ST = "ST", "Delantero"

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=120)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=60, blank=True)
    preferred_foot = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=5, choices=Position.choices)

    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    current_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
        help_text="Equipo habitual/actual del jugador. No sustituye convocatorias temporales.",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class PlayerSeasonStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="season_stats")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="player_stats")

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_season_stats",
        help_text="Equipo con el que se registran estas estadísticas en esa temporada.",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_season_stats",
        help_text="Competición específica si quieres separar liga, copa, mundial, etc.",
    )

    minutes_played = models.PositiveIntegerField(default=0)
    matches_played = models.PositiveIntegerField(default=0)
    starts = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)

    xg = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    xa = models.DecimalField(max_digits=8, decimal_places=3, default=0)

    class Meta:
        unique_together = ("player", "season", "team", "competition")
        ordering = ["-season__start_date", "player__last_name"]

    def __str__(self) -> str:
        parts = [str(self.player), str(self.season)]
        if self.team:
            parts.append(str(self.team))
        if self.competition:
            parts.append(str(self.competition))
        return " - ".join(parts)


class NationalTeamCallUp(models.Model):
    """
    Convocatoria de jugador para una selección en una competición,
    ventana internacional o periodo concreto.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="national_callups")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="callups",
        limit_choices_to={
            "team_type__in": [
                Team.TeamType.NATIONAL,
                Team.TeamType.YOUTH_NATIONAL,
                Team.TeamType.WOMEN_NATIONAL,
            ]
        },
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="national_callups",
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    squad_role = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ej.: titular, suplente, prelista, reserva.",
    )
    shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    called_up_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registered_callups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "team__name", "player__last_name"]

    def __str__(self) -> str:
        comp = f" | {self.competition}" if self.competition else ""
        return f"{self.player} | {self.team}{comp}"


class InjuryRecord(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="injuries")
    diagnosis = models.CharField(max_length=200)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.LOW)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    days_out = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_injuries",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.player} - {self.diagnosis}"