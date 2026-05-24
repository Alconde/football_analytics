from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.views.generic import TemplateView

from apps.analytics.services import PlotlyService
from apps.kpi.models import MatchKPI
from apps.matches.models import Match, MatchTeamStat
from apps.players.models import Player
from apps.reports.models import GeneratedReport


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["upcoming_matches"] = (
            Match.objects.filter(status=Match.Status.SCHEDULED)
            .select_related("home_team", "away_team", "competition")
            .order_by("match_date")[:5]
        )
        ctx["recent_matches"] = (
            Match.objects.filter(status=Match.Status.FINISHED)
            .select_related("home_team", "away_team")
            .order_by("-match_date")[:5]
        )
        ctx["players_count"] = Player.objects.filter(is_active=True).count()
        ctx["recent_reports"] = GeneratedReport.objects.select_related(
            "match", "team", "player", "generated_by"
        ).order_by("-generated_at")[:5]

        ctx["matches_finished"] = Match.objects.filter(status=Match.Status.FINISHED).count()
        ctx["matches_scheduled"] = len(ctx["upcoming_matches"])
        ctx["kpi_entries"] = MatchKPI.objects.filter(match__status=Match.Status.FINISHED).count()

        kpi_average = (
            MatchKPI.objects.filter(match__status=Match.Status.FINISHED)
            .values("kpi_type__code")
            .annotate(avg_value=Avg("value"))
            .order_by("kpi_type__code")
        )

        ctx["kpi_summary"] = [
            {
                "code": row["kpi_type__code"].upper(),
                "value": float(row["avg_value"] or 0),
            }
            for row in kpi_average
        ]

        if ctx["kpi_summary"]:
            labels = [row["code"] for row in ctx["kpi_summary"]]
            values = [row["value"] for row in ctx["kpi_summary"]]
            ctx["kpi_summary_chart"] = PlotlyService.get_kpi_summary_bar(
                labels, values, title="KPIs promedio de partidos finalizados"
            )
        else:
            ctx["kpi_summary_chart"] = ""

        recent_team_stats = list(
            MatchTeamStat.objects.filter(match__status=Match.Status.FINISHED)
            .values("match__match_date")
            .annotate(
                avg_xg=Avg("xg"),
                avg_possession=Avg("possession_pct"),
                avg_ppda=Avg("ppda"),
            )
            .order_by("-match__match_date")[:6]
        )

        if recent_team_stats:
            recent_team_stats.reverse()
            labels = [stat["match__match_date"].strftime("%d/%m") for stat in recent_team_stats]
            xg_values = [float(stat["avg_xg"] or 0) for stat in recent_team_stats]
            possession_values = [float(stat["avg_possession"] or 0) for stat in recent_team_stats]
            ppda_values = [float(stat["avg_ppda"] or 0) for stat in recent_team_stats]
            ctx["trend_chart_html"] = PlotlyService.get_match_kpi_trend(
                labels, xg_values, possession_values, ppda_values
            )
        else:
            ctx["trend_chart_html"] = ""

        return ctx
