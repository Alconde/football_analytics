"""
Datos de demostración: 1 club + rival, 2 equipos, 1 temporada, 1 competición,
22 jugadores, 4 partidos. Idempotente: si ya existen por nombre, no duplica club/temporada/competición.
"""
from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from apps.clubs.models import Club, Competition, Season, Team, TeamSeason
from apps.players.models import Player
from apps.matches.models import Match

# --- Clubes ---
club_own, _ = Club.objects.get_or_create(
    name="Club Deportivo Atlántico",
    defaults={
        "short_name": "CD Atlántico",
        "country": "España",
        "city": "Vigo",
        "founded_year": 1998,
    },
)
club_rival, _ = Club.objects.get_or_create(
    name="Unión Deportiva Ribera",
    defaults={
        "short_name": "UD Ribera",
        "country": "España",
        "city": "Ourense",
        "founded_year": 2005,
    },
)

# --- Temporada ---
season, _ = Season.objects.get_or_create(
    name="2025/2026",
    defaults={
        "start_date": date(2025, 7, 1),
        "end_date": date(2026, 6, 30),
        "is_active": True,
    },
)

# --- Competición ---
comp, _ = Competition.objects.get_or_create(
    name="Segunda Federación – Grupo I",
    defaults={"country": "España", "level": "4ª categoría nacional"},
)

# --- Equipos ---
team_own, _ = Team.objects.get_or_create(
    club=club_own,
    name="Primer equipo",
    defaults={"category": Team.Category.FIRST_TEAM},
)
team_rival, _ = Team.objects.get_or_create(
    club=club_rival,
    name="Primer equipo",
    defaults={"category": Team.Category.FIRST_TEAM},
)

TeamSeason.objects.get_or_create(
    team=team_own,
    season=season,
    competition=comp,
    defaults={"coach_name": "Marcos Valdés"},
)
TeamSeason.objects.get_or_create(
    team=team_rival,
    season=season,
    competition=comp,
    defaults={"coach_name": "Laura Méndez"},
)

# --- Plantilla (22 jugadores) ---
# (nombre, apellidos, posición, dorsal lógico vía orden, pie, altura, peso)
roster = [
    ("Iker", "Souto", Player.Position.GK, "derecha", 188, Decimal("82.5")),
    ("Nico", "Pazos", Player.Position.GK, "derecha", 186, Decimal("80.0")),
    ("Hugo", "Varela", Player.Position.CB, "derecha", 190, Decimal("86.0")),
    ("Álex", "Ferreiro", Player.Position.CB, "izquierda", 187, Decimal("84.0")),
    ("Diego", "Montes", Player.Position.CB, "derecha", 185, Decimal("83.0")),
    ("Pablo", "Insua", Player.Position.FB, "derecha", 178, Decimal("74.0")),
    ("Javi", "Romero", Player.Position.FB, "izquierda", 176, Decimal("72.0")),
    ("Samu", "Costa", Player.Position.DM, "derecha", 182, Decimal("78.0")),
    ("Bruno", "Neves", Player.Position.CM, "derecha", 180, Decimal("76.0")),
    ("Mario", "Silva", Player.Position.CM, "izquierda", 178, Decimal("75.0")),
    ("Lucas", "Peralta", Player.Position.AM, "derecha", 174, Decimal("70.0")),
    ("Andrés", "Teijeira", Player.Position.WG, "izquierda", 176, Decimal("71.0")),
    ("Iago", "Baltar", Player.Position.WG, "derecha", 175, Decimal("72.0")),
    ("Héctor", "Lema", Player.Position.ST, "derecha", 183, Decimal("81.0")),
    ("Álvaro", "Seoane", Player.Position.ST, "izquierda", 181, Decimal("79.0")),
    ("Martín", "Couce", Player.Position.FB, "derecha", 179, Decimal("73.0")),
    ("Tomi", "Fuentes", Player.Position.DM, "derecha", 181, Decimal("77.0")),
    ("Guille", "Ríos", Player.Position.CM, "derecha", 177, Decimal("74.0")),
    ("Nacho", "Piñeiro", Player.Position.AM, "izquierda", 173, Decimal("69.0")),
    ("Sergio", "Taboada", Player.Position.WG, "derecha", 174, Decimal("70.0")),
    ("Rubén", "Caride", Player.Position.CB, "derecha", 188, Decimal("85.0")),
    ("Adri", "Lorenzo", Player.Position.ST, "derecha", 184, Decimal("82.0")),
]

created_players = 0
for fn, ln, pos, foot, h, w in roster:
    p, created = Player.objects.get_or_create(
        first_name=fn,
        last_name=ln,
        defaults={
            "birth_date": date(2000, 5, 15),
            "nationality": "España",
            "preferred_foot": foot,
            "position": pos,
            "height_cm": h,
            "weight_kg": w,
            "current_team": team_own,
            "is_active": True,
        },
    )
    if created:
        created_players += 1

# Asegurar que todos queden en el equipo actual
Player.objects.filter(
    first_name__in=[r[0] for r in roster],
    last_name__in=[r[1] for r in roster],
).update(current_team=team_own, is_active=True)

# --- Partidos (4) ---
# Usar timezone aware para consistencia con USE_TZ
def dt(y, m, d, hh, mm):
    return timezone.make_aware(datetime(y, m, d, hh, mm))

fixtures = [
    # local, rival es visitante, fecha, local_goals, away_goals, status
    (team_own, team_rival, dt(2025, 8, 17, 19, 0), 2, 1, Match.Status.FINISHED, "Estadio Municipal de Bouzas"),
    (team_rival, team_own, dt(2025, 9, 1, 18, 30), 0, 1, Match.Status.FINISHED, "Campo A Lomba"),
    (team_own, team_rival, dt(2025, 9, 21, 17, 0), 1, 1, Match.Status.FINISHED, "Estadio Municipal de Bouzas"),
    (team_rival, team_own, dt(2025, 10, 12, 19, 0), None, None, Match.Status.SCHEDULED, "Campo A Lomba"),
]

for home, away, when, hg, ag, st, venue in fixtures:
    Match.objects.get_or_create(
        season=season,
        competition=comp,
        match_date=when,
        home_team=home,
        away_team=away,
        defaults={
            "home_score": hg,
            "away_score": ag,
            "status": st,
            "venue": venue,
        },
    )

print("OK demo:")
print(" club_own=", club_own.name)
print(" team_own=", team_own)
print(" season=", season.name)
print(" players_created=", created_players, "(nuevos en esta ejecución)")
print(" matches total season=", Match.objects.filter(season=season).count())