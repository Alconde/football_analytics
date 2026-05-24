"""
Managers personalizados para modelos.
Los managers definen queries reutilizables.
"""
from django.db import models
from django.db.models import Prefetch, Q, Count, Avg


class BaseQuerySet(models.QuerySet):
    """QuerySet base con métodos comunes"""
    
    def active(self):
        """Filtro para registros activos (si existe campo 'is_active')"""
        if 'is_active' in [f.name for f in self.model._meta.get_fields()]:
            return self.filter(is_active=True)
        return self
    
    def ordered(self):
        """Ordena por el campo 'order' si existe"""
        if 'order' in [f.name for f in self.model._meta.get_fields()]:
            return self.order_by('order')
        return self
    
    def with_counts(self, **counts):
        """
        Agregar conteos a los resultados.
        
        Ejemplo:
            Team.objects.with_counts(players=Count('players'))
        """
        for field_name, annotation in counts.items():
            self = self.annotate(**{field_name: annotation})
        return self


class BaseManager(models.Manager):
    """Manager base con métodos comunes"""
    
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)
    
    def active(self):
        """Filtro para registros activos"""
        return self.get_queryset().active()
    
    def ordered(self):
        """Ordena por 'order' si existe"""
        return self.get_queryset().ordered()
    
    def with_counts(self, **counts):
        """Agregar conteos"""
        return self.get_queryset().with_counts(**counts)


# ============================================================================
# MANAGERS ESPECIALIZADOS POR DOMINIO
# ============================================================================

class ClubManager(BaseManager):
    """Manager para Clubs"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('teams')
    
    def with_team_count(self):
        """Agregar conteo de equipos"""
        return self.get_queryset().annotate(team_count=Count('teams'))
    
    def with_active_teams(self):
        """Prefetch de equipos activos"""
        from apps.clubs.models import Team
        active_teams = Team.objects.filter(is_active=True)
        return self.prefetch_related(
            Prefetch('teams', queryset=active_teams)
        )


class TeamManager(BaseManager):
    """Manager para Teams"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('club')
    
    def by_club(self, club):
        """Filtrar por club"""
        return self.filter(club=club)
    
    def with_player_count(self):
        """Agregar conteo de jugadores"""
        return self.annotate(player_count=Count('players'))
    
    def with_stats(self):
        """Incluir estadísticas del equipo"""
        return self.annotate(
            total_matches=Count('home_matches') + Count('away_matches'),
            total_wins=Count(
                'home_matches',
                filter=Q(home_matches__home_score__gt=models.F('home_matches__away_score'))
            )
        )


class PlayerManager(BaseManager):
    """Manager para Players"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('current_team').prefetch_related('season_stats', 'injuries')
    
    def by_position(self, position):
        """Filtrar por posición"""
        return self.filter(position=position)
    
    def by_team(self, team):
        """Filtrar por equipo"""
        return self.filter(team=team)
    
    def injured(self):
        """Solo jugadores lesionados"""
        from apps.players.models import InjuryRecord
        return self.filter(
            injury_records__return_date__isnull=True
        ).distinct()
    
    def active(self):
        """Solo jugadores activos"""
        return self.filter(is_active=True)
    
    def with_stats(self):
        """Incluir estadísticas agregadas"""
        return self.annotate(
            total_minutes=models.Sum('season_stats__minutes_played'),
            avg_rating=models.Avg('season_stats__rating'),
            total_matches=Count('season_stats')
        )


class MatchManager(BaseManager):
    """Manager para Matches"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'home_team', 'away_team', 'season', 'competition'
        ).prefetch_related('team_stats', 'kpis')
    
    def finished(self):
        """Solo partidos finalizados"""
        from apps.matches.models import Match
        return self.filter(status=Match.Status.FINISHED)
    
    def upcoming(self):
        """Solo partidos futuros"""
        from apps.matches.models import Match
        return self.filter(status=Match.Status.SCHEDULED)
    
    def by_team(self, team):
        """Partidos de un equipo (como local o visitante)"""
        return self.filter(
            Q(home_team=team) | Q(away_team=team)
        )
    
    def by_season(self, season):
        """Filtrar por temporada"""
        return self.filter(season=season)
    
    def with_kpis(self):
        """Incluir KPIs agregados"""
        from apps.kpi.models import MatchKPI
        kpis = MatchKPI.objects.values('match').annotate(
            total_kpis=Count('id')
        )
        return self.annotate(
            total_kpis=Count('kpis')
        )


class KPIManager(BaseManager):
    """Manager para KPIs"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        related_fields = ["match", "kpi_type"]
        model_field_names = [f.name for f in self.model._meta.get_fields()]
        if "player" in model_field_names:
            related_fields.append("player")
        if "team" in model_field_names:
            related_fields.append("team")
        return qs.select_related(*related_fields)
    
    def by_type(self, kpi_type):
        """Filtrar por tipo de KPI"""
        return self.filter(kpi_type=kpi_type)
    
    def by_match(self, match):
        """Filtrar por partido"""
        return self.filter(match=match)
    
    def by_player(self, player):
        """Filtrar por jugador"""
        return self.filter(player=player)
    
    def by_team(self, team):
        """Filtrar por equipo"""
        return self.filter(
            Q(match__home_team=team) | Q(match__away_team=team)
        )
    
    def aggregate_by_match(self):
        """Agregar KPIs por partido"""
        return self.values('match').annotate(
            avg_value=Avg('value'),
            max_value=models.Max('value'),
            min_value=models.Min('value')
        )
    
    def aggregate_by_player(self):
        """Agregar KPIs por jugador"""
        return self.values('player').annotate(
            avg_value=Avg('value'),
            max_value=models.Max('value'),
            total_matches=Count('match', distinct=True)
        )


class ReportManager(BaseManager):
    """Manager para Reports"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('match', 'team', 'player', 'generated_by')
    
    def pending(self):
        """Reportes pendientes de generación"""
        from apps.reports.models import GeneratedReport
        return self.filter(status=GeneratedReport.Status.PENDING)
    
    def completed(self):
        """Reportes completados"""
        from apps.reports.models import GeneratedReport
        return self.filter(status=GeneratedReport.Status.COMPLETED)
    
    def by_user(self, user):
        """Reportes generados por un usuario"""
        return self.filter(generated_by=user)
    
    def recent(self, days=7):
        """Reportes recientes (últimos N días)"""
        from django.utils import timezone
        from datetime import timedelta
        
        date_since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=date_since)