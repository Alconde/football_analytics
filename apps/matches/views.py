from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

import plotly.graph_objects as go
from plotly.offline import plot

from apps.kpi.models import MatchKPI
from .forms import MatchForm
from .models import Match, MatchTeamStat


class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "matches/match_list.html"
    context_object_name = "matches"
    paginate_by = 20

    def get_queryset(self):
        return (
            Match.objects.select_related(
                "season",
                "competition",
                "home_team",
                "away_team",
            )
            .order_by("-match_date")
        )


class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm
    template_name = "matches/match_form.html"
    success_url = reverse_lazy("matches:list")


class MatchAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "matches/match_analytics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        match = get_object_or_404(
            Match.objects.select_related(
                "season",
                "competition",
                "home_team",
                "away_team",
            ),
            pk=self.kwargs["pk"],
        )

        ctx["match"] = match

        stats = {
            stat.team_id: stat
            for stat in MatchTeamStat.objects.filter(match=match).select_related("team")
        }

        home_stat = stats.get(match.home_team_id)
        away_stat = stats.get(match.away_team_id)

        ctx["home_stat"] = home_stat
        ctx["away_stat"] = away_stat

        missing_stats = not home_stat or not away_stat
        ctx["missing_stats"] = missing_stats

        ctx["chart_html"] = ""
        ctx["radar_chart_html"] = ""
        ctx["has_radar"] = False
        ctx["kpi_chart_html"] = ""
        ctx["has_kpi_chart"] = False

        if not missing_stats:
            basic_metrics = [
                ("Posesión", float(home_stat.possession_pct or 0), float(away_stat.possession_pct or 0)),
                ("xG", float(home_stat.xg or 0), float(away_stat.xg or 0)),
                ("Tiros", float(home_stat.shots or 0), float(away_stat.shots or 0)),
                ("Tiros a puerta", float(home_stat.shots_on_target or 0), float(away_stat.shots_on_target or 0)),
                ("Recuperaciones", float(home_stat.recoveries or 0), float(away_stat.recoveries or 0)),
            ]

            labels = [metric[0] for metric in basic_metrics]
            home_values = [metric[1] for metric in basic_metrics]
            away_values = [metric[2] for metric in basic_metrics]

            fig = go.Figure(
                data=[
                    go.Bar(
                        name=str(match.home_team),
                        x=labels,
                        y=home_values,
                        marker_color="#34d399",
                    ),
                    go.Bar(
                        name=str(match.away_team),
                        x=labels,
                        y=away_values,
                        marker_color="#60a5fa",
                    ),
                ]
            )

            fig.update_layout(
                barmode="group",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.9)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=40, r=20, t=50, b=40),
                title="Comparativa básica del partido",
            )

            ctx["chart_html"] = plot(fig, output_type="div", include_plotlyjs=False)

            def scale_pair(home_value, away_value, lower_is_better=False):
                home_value = float(home_value or 0)
                away_value = float(away_value or 0)

                if lower_is_better:
                    home_value = 1 / (home_value + 1e-6)
                    away_value = 1 / (away_value + 1e-6)

                max_value = max(home_value, away_value, 1e-6)
                return (100.0 * home_value / max_value, 100.0 * away_value / max_value)

            hp, ap = scale_pair(home_stat.possession_pct, away_stat.possession_pct)
            hpa, apa = scale_pair(home_stat.pass_accuracy_pct, away_stat.pass_accuracy_pct)
            hxg, axg = scale_pair(home_stat.xg, away_stat.xg)
            hs, ass_ = scale_pair(home_stat.shots, away_stat.shots)
            hr, ar = scale_pair(home_stat.recoveries, away_stat.recoveries)

            radar_categories = ["Posesión", "Precisión pase", "xG", "Tiros", "Recuperaciones"]
            home_radar = [hp, hpa, hxg, hs, hr]
            away_radar = [ap, apa, axg, ass_, ar]

            radar_fig = go.Figure()

            radar_fig.add_trace(
                go.Scatterpolar(
                    r=home_radar,
                    theta=radar_categories,
                    fill="toself",
                    name=str(match.home_team),
                    line_color="#34d399",
                )
            )
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=away_radar,
                    theta=radar_categories,
                    fill="toself",
                    name=str(match.away_team),
                    line_color="#60a5fa",
                )
            )

            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                title="Radar comparativo del partido",
                margin=dict(l=40, r=40, t=60, b=40),
            )

            ctx["radar_chart_html"] = plot(radar_fig, output_type="div", include_plotlyjs=False)
            ctx["has_radar"] = True

        kpi_rows = (
            MatchKPI.objects.filter(match=match)
            .select_related("team", "kpi_type")
            .order_by("kpi_type__code", "team_id")
        )

        kpi_types = []
        home_map = {}
        away_map = {}

        for row in kpi_rows:
            code = row.kpi_type.code

            if code not in kpi_types:
                kpi_types.append(code)

            if row.team_id == match.home_team_id:
                home_map[code] = float(row.value)
            elif row.team_id == match.away_team_id:
                away_map[code] = float(row.value)

        usable_codes = [code for code in sorted(kpi_types) if code in home_map and code in away_map]

        if usable_codes:
            labels = [code.upper() for code in usable_codes]
            home_values = [home_map[code] for code in usable_codes]
            away_values = [away_map[code] for code in usable_codes]

            kpi_fig = go.Figure(
                data=[
                    go.Bar(
                        name=str(match.home_team),
                        x=labels,
                        y=home_values,
                        marker_color="#34d399",
                    ),
                    go.Bar(
                        name=str(match.away_team),
                        x=labels,
                        y=away_values,
                        marker_color="#60a5fa",
                    ),
                ]
            )

            kpi_fig.update_layout(
                barmode="group",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.9)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=40, r=20, t=50, b=40),
                title="KPIs registrados del partido",
            )

            ctx["kpi_chart_html"] = plot(kpi_fig, output_type="div", include_plotlyjs=False)
            ctx["has_kpi_chart"] = True

        return ctx