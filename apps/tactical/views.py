from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from apps.core.staff_role_mixins import RoleRequiredMixin
from apps.users.models import User
from .forms import TacticalReportForm
from .models import TacticalReport
from apps.matches.models import Match
from apps.clubs.models import Season, Team
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View






class TacticalReportListView(RoleRequiredMixin, ListView):
    allowed_roles = ()
    model = TacticalReport
    template_name = "tactical/tacticalreport_list.html"
    context_object_name = "reports"
    paginate_by = 20

    def _teams_for_user(self):
        """
        Equipos del club: si el usuario tiene club_name, filtra por nombre de club;
        si no, muestra todos los equipos (MVP).
        """
        qs = Team.objects.select_related("club").order_by("club__name", "name")
        club_name = getattr(self.request.user, "club_name", "") or ""
        club_name = club_name.strip()
        if club_name:
            return qs.filter(
                Q(club__name__icontains=club_name) | Q(club__short_name__icontains=club_name)
            )
        return qs

    def _default_season(self):
        active = Season.objects.filter(is_active=True).order_by("-start_date").first()
        if active:
            return active
        return Season.objects.order_by("-start_date").first()

    def get_queryset(self):
        qs = (
            TacticalReport.objects.select_related(
                "match",
                "team",
                "team__club",
                "created_by",
                "match__season",
                "match__competition",
                "match__home_team",
                "match__away_team",
            )
            .prefetch_related("phase_observations")
            .order_by("-created_at")
        )

        season_id = (self.request.GET.get("season") or "").strip()
        match_id = (self.request.GET.get("match") or "").strip()
        team_id = (self.request.GET.get("team") or "").strip()
        focus = (self.request.GET.get("focus") or "").strip()
        q = (self.request.GET.get("q") or "").strip()

        if team_id.isdigit():
            qs = qs.filter(team_id=int(team_id))
        if match_id.isdigit():
            qs = qs.filter(match_id=int(match_id))
        elif season_id.isdigit():
            qs = qs.filter(match__season_id=int(season_id))

        if focus in ("own", "opponent"):
            qs = qs.filter(team_focus=focus)

        if q:
            qs = qs.filter(
                Q(system_used__icontains=q)
                | Q(strengths__icontains=q)
                | Q(weaknesses__icontains=q)
                | Q(recurring_errors__icontains=q)
                | Q(coach_notes__icontains=q)
                | Q(team__name__icontains=q)
                | Q(match__home_team__name__icontains=q)
                | Q(match__away_team__name__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        season_id = (self.request.GET.get("season") or "").strip()
        match_id = (self.request.GET.get("match") or "").strip()
        team_id = (self.request.GET.get("team") or "").strip()
        focus = (self.request.GET.get("focus") or "").strip()
        q = (self.request.GET.get("q") or "").strip()

        seasons = Season.objects.order_by("-start_date")
        default_season = self._default_season()

        if not season_id and default_season:
            season_id = str(default_season.id)

        matches = Match.objects.none()
        if season_id.isdigit():
            matches = (
                Match.objects.filter(season_id=int(season_id))
                .select_related("home_team", "away_team", "competition")
                .order_by("match_date")
            )

        teams = self._teams_for_user()

        ctx["seasons"] = seasons
        ctx["matches"] = matches
        ctx["teams"] = teams

        ctx["filters"] = {
            "season": season_id,
            "match": match_id,
            "team": team_id,
            "focus": focus,
            "q": q,
        }
        return ctx


class TacticalReportDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ()
    model = TacticalReport
    template_name = "tactical/tacticalreport_detail.html"
    context_object_name = "report"

    def get_queryset(self):
        return TacticalReport.objects.select_related(
            "match",
            "team",
            "team__club",
            "created_by",
            "match__season",
            "match__competition",
            "match__home_team",
            "match__away_team",
        ).prefetch_related("phase_observations")


class TacticalReportCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (User.Role.ADMIN, User.Role.TACTICAL_ANALYST)
    model = TacticalReport
    form_class = TacticalReportForm
    template_name = "tactical/tacticalreport_form.html"
    success_url = reverse_lazy("tactical:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MatchSelectFragmentView(LoginRequiredMixin, View):
    """
    Devuelve HTML parcial con el desplegable de partidos para una temporada.
    HTMX hace GET con ?season=<id>
    """

    def get(self, request):
        season_id = (request.GET.get("season") or "").strip()
        selected_match = (request.GET.get("match") or "").strip()

        matches = Match.objects.none()
        if season_id.isdigit():
            matches = (
                Match.objects.filter(season_id=int(season_id))
                .select_related("home_team", "away_team", "competition")
                .order_by("match_date")
            )

        return render(
            request,
            "tactical/partials/match_select.html",
            {
                "matches": matches,
                "selected_match": selected_match,
            },
        )