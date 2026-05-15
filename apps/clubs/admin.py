from django.contrib import admin
from .models import Club, Competition, Season, Team, TeamSeason


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "entity_type",
        "country",
        "city",
        "confederation",
        "fifa_code",
        "is_national_entity",
        "founded_year",
    )
    list_filter = (
        "entity_type",
        "is_national_entity",
        "country",
        "confederation",
    )
    search_fields = (
        "name",
        "short_name",
        "country",
        "city",
        "fifa_code",
    )
    ordering = ("name",)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "competition_type",
        "country",
        "level",
        "organizer",
        "is_national_teams",
    )
    list_filter = (
        "competition_type",
        "is_national_teams",
        "country",
        "organizer",
    )
    search_fields = (
        "name",
        "country",
        "level",
        "organizer",
    )
    ordering = ("name",)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("-start_date",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "club",
        "team_type",
        "category",
        "gender",
        "country",
        "fifa_ranking",
        "is_active",
    )
    list_filter = (
        "team_type",
        "category",
        "gender",
        "is_active",
        "country",
        "club",
    )
    search_fields = (
        "name",
        "short_name",
        "club__name",
        "club__short_name",
        "country",
    )
    autocomplete_fields = ("club",)
    ordering = ("club__name", "name")


@admin.register(TeamSeason)
class TeamSeasonAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "season",
        "competition",
        "coach_name",
        "squad_label",
    )
    list_filter = (
        "season",
        "competition",
        "team__team_type",
        "team__gender",
        "team__country",
    )
    search_fields = (
        "team__name",
        "team__short_name",
        "team__club__name",
        "season__name",
        "competition__name",
        "coach_name",
        "squad_label",
    )
    autocomplete_fields = ("team", "season", "competition")
    ordering = ("-season__start_date", "team__name")