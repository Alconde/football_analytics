from django.contrib import admin
from .models import Player, PlayerSeasonStat, InjuryRecord, NationalTeamCallUp


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "position",
        "nationality",
        "preferred_foot",
        "current_team",
        "is_active",
        "created_at",
    )
    list_filter = (
        "position",
        "is_active",
        "nationality",
        "current_team__team_type",
        "current_team__gender",
    )
    search_fields = (
        "first_name",
        "last_name",
        "nationality",
        "current_team__name",
        "current_team__club__name",
    )
    autocomplete_fields = ("current_team",)
    ordering = ("last_name", "first_name")


@admin.register(PlayerSeasonStat)
class PlayerSeasonStatAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "season",
        "team",
        "competition",
        "matches_played",
        "minutes_played",
        "goals",
        "assists",
        "xg",
        "xa",
    )
    list_filter = (
        "season",
        "competition",
        "team__team_type",
        "team__country",
    )
    search_fields = (
        "player__first_name",
        "player__last_name",
        "season__name",
        "team__name",
        "competition__name",
    )
    autocomplete_fields = ("player", "season", "team", "competition")
    ordering = ("-season__start_date", "player__last_name")


@admin.register(NationalTeamCallUp)
class NationalTeamCallUpAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "team",
        "competition",
        "start_date",
        "end_date",
        "squad_role",
        "shirt_number",
        "called_up_by",
    )
    list_filter = (
        "team",
        "competition",
        "start_date",
        "team__country",
    )
    search_fields = (
        "player__first_name",
        "player__last_name",
        "team__name",
        "team__club__name",
        "competition__name",
        "notes",
    )
    autocomplete_fields = ("player", "team", "competition", "called_up_by")
    ordering = ("-start_date", "team__name", "player__last_name")


@admin.register(InjuryRecord)
class InjuryRecordAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "diagnosis",
        "severity",
        "start_date",
        "end_date",
        "days_out",
        "reported_by",
    )
    list_filter = ("severity", "start_date", "end_date")
    search_fields = (
        "player__first_name",
        "player__last_name",
        "diagnosis",
        "notes",
    )
    autocomplete_fields = ("player", "reported_by")
    ordering = ("-start_date",)