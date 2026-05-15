from django.db import models


class Club(models.Model):
    """
    Se mantiene el nombre 'Club' por compatibilidad con el proyecto actual,
    pero funcionalmente representa cualquier organización futbolística:
    club, federación, asociación nacional, academia, etc.
    """

    class EntityType(models.TextChoices):
        CLUB = "club", "Club"
        FEDERATION = "federation", "Federación"
        ASSOCIATION = "association", "Asociación nacional"
        ACADEMY = "academy", "Academia"
        OTHER = "other", "Otra"

    name = models.CharField(max_length=120, unique=True)
    short_name = models.CharField(max_length=30, blank=True)
    entity_type = models.CharField(
        max_length=20,
        choices=EntityType.choices,
        default=EntityType.CLUB,
    )

    country = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=60, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    fifa_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="Útil para selecciones/federaciones: ESP, ARG, FRA, etc.",
    )
    confederation = models.CharField(
        max_length=30,
        blank=True,
        help_text="UEFA, CONMEBOL, CONCACAF, CAF, AFC, OFC...",
    )

    is_national_entity = models.BooleanField(
        default=False,
        help_text="Marca si esta organización representa una estructura nacional.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Competition(models.Model):
    class CompetitionType(models.TextChoices):
        LEAGUE = "league", "Liga"
        CUP = "cup", "Copa"
        INTERNATIONAL_CLUB = "international_club", "Internacional de clubes"
        INTERNATIONAL_NATIONAL = "international_national", "Internacional de selecciones"
        FRIENDLY = "friendly", "Amistoso"
        OTHER = "other", "Otra"

    name = models.CharField(max_length=120, unique=True)
    country = models.CharField(max_length=60, blank=True)
    level = models.CharField(max_length=40, blank=True)
    competition_type = models.CharField(
        max_length=30,
        choices=CompetitionType.choices,
        default=CompetitionType.LEAGUE,
    )
    organizer = models.CharField(
        max_length=120,
        blank=True,
        help_text="Ej.: FIFA, UEFA, RFEF, LaLiga...",
    )
    is_national_teams = models.BooleanField(
        default=False,
        help_text="Marca si la competición es de selecciones nacionales.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name


class Team(models.Model):
    class Category(models.TextChoices):
        FIRST_TEAM = "first_team", "Primer equipo"
        U23 = "u23", "Sub-23"
        U21 = "u21", "Sub-21"
        U20 = "u20", "Sub-20"
        U19 = "u19", "Sub-19"
        U17 = "u17", "Sub-17"
        U16 = "u16", "Sub-16"
        WOMEN_FIRST = "women_first", "Femenino primer equipo"

    class TeamType(models.TextChoices):
        CLUB = "club", "Equipo de club"
        NATIONAL = "national", "Selección nacional"
        YOUTH_NATIONAL = "youth_national", "Selección inferior"
        WOMEN_NATIONAL = "women_national", "Selección femenina"
        ACADEMY = "academy", "Academia"
        OTHER = "other", "Otro"

    class Gender(models.TextChoices):
        MALE = "male", "Masculino"
        FEMALE = "female", "Femenino"
        MIXED = "mixed", "Mixto"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="teams",
        help_text="Se mantiene el nombre del campo por compatibilidad.",
    )
    name = models.CharField(max_length=120)
    short_name = models.CharField(max_length=40, blank=True)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.FIRST_TEAM,
    )
    team_type = models.CharField(
        max_length=20,
        choices=TeamType.choices,
        default=TeamType.CLUB,
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
    )

    country = models.CharField(
        max_length=60,
        blank=True,
        help_text="Útil especialmente para selecciones.",
    )
    fifa_ranking = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("club", "name")
        ordering = ["club__name", "name"]

    def __str__(self) -> str:
        return f"{self.club.name} - {self.name}"

    @property
    def is_national_team(self) -> bool:
        return self.team_type in {
            self.TeamType.NATIONAL,
            self.TeamType.YOUTH_NATIONAL,
            self.TeamType.WOMEN_NATIONAL,
        }


class TeamSeason(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="season_links")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="team_links")
    competition = models.ForeignKey(
        Competition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_seasons",
    )
    coach_name = models.CharField(max_length=120, blank=True)

    squad_label = models.CharField(
        max_length=120,
        blank=True,
        help_text="Ej.: Plantilla Mundial 2026, Plantilla Nations League, Primer equipo 2025/26.",
    )

    class Meta:
        unique_together = ("team", "season", "competition")
        ordering = ["-season__start_date", "team__name"]

    def __str__(self) -> str:
        comp = self.competition.name if self.competition else "Sin competición"
        return f"{self.team} | {self.season} | {comp}"