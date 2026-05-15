from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from apps.core.staff_role_mixins import RoleRequiredMixin
from apps.users.models import User

from .forms import PlayerForm
from .models import Player
from apps.analytics.services import PlotlyService 

class PlayerListView(RoleRequiredMixin, ListView):
    allowed_roles = ()
    model = Player
    template_name = "players/player_list.html"
    context_object_name = "players"
    paginate_by = 25

    def get_queryset(self):
        qs = (
            Player.objects.select_related("current_team", "current_team__club")
            .order_by("last_name", "first_name")
        )

        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(nationality__icontains=q)
                | Q(current_team__name__icontains=q)
                | Q(current_team__club__name__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        return ctx


class PlayerCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (
        User.Role.ADMIN,
        User.Role.TACTICAL_ANALYST,
        User.Role.DATA_ANALYST,
        User.Role.SCOUT,
    )
    model = Player
    form_class = PlayerForm
    template_name = "players/player_form.html"
    success_url = reverse_lazy("players:list")


class PlayerUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = (
        User.Role.ADMIN,
        User.Role.TACTICAL_ANALYST,
        User.Role.DATA_ANALYST,
        User.Role.SCOUT,
    )
    model = Player
    form_class = PlayerForm
    template_name = "players/player_form.html"
    success_url = reverse_lazy("players:list")



class PlayerDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = () # Todos los roles pueden ver detalles
    model = Player
    template_name = "players/player_detail.html"
    context_object_name = "player"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Datos temporales para la Fase 4 (0.0 a 1.0)
        # En la Fase 5 esto vendrá de modelos de datos reales
        mock_stats = {
            'xG/90': 0.72,
            'Pases Prog.': 0.85,
            'Duelos Ganados': 0.40,
            'Recuperaciones': 0.30,
            'Toques Area': 0.90,
            'Asistencias': 0.55
        }
        
        # Generamos el gráfico usando el servicio de la app analytics
        ctx['radar_chart'] = PlotlyService.get_player_radar(mock_stats, self.object.first_name())
        return ctx