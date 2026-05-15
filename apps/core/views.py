from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.matches.models import Match
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
        return ctx
