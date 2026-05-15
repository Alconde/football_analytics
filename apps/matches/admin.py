from django.contrib import admin
from .models import Match, MatchTeamStat


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "match_date",
        "season",
        "competition",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "status",
        "venue",
    )
    list_filter = (
        "status",
        "season",
        "competition",
        "home_team__team_type",
        "away_team__team_type",
        "competition__is_national_teams",
    )
    search_fields = (
        "home_team__name",
        "home_team__short_name",
        "home_team__club__name",
        "away_team__name",
        "away_team__short_name",
        "away_team__club__name",
        "competition__name",
        "venue",
    )
    autocomplete_fields = (
        "season",
        "competition",
        "home_team",
        "away_team",
    )
    ordering = ("-match_date",)


@admin.register(MatchTeamStat)
class MatchTeamStatAdmin(admin.ModelAdmin):
    list_display = (
        "match",
        "team",
        "possession_pct",
        "xg",
        "shots",
        "shots_on_target",
        "passes",
        "pass_accuracy_pct",
        "ppda",
        "recoveries",
    )
    list_filter = (
        "match__season",
        "match__competition",
        "team__team_type",
        "team__country",
        "team",
    )
    search_fields = (
        "team__name",
        "team__short_name",
        "team__club__name",
        "match__home_team__name",
        "match__away_team__name",
        "match__competition__name",
    )
    autocomplete_fields = (
        "match",
        "team",
    )
    ordering = ("-match__match_date", "team__name")