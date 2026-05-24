from datetime import datetime
from decimal import Decimal

from django.utils import timezone

from apps.clubs.models import Club, Competition, Season, Team, TeamSeason
from apps.matches.models import Match, MatchTeamStat
from apps.players.models import Player, NationalTeamCallUp


def dt(y, m, d, hh=20, mm=0):
    return timezone.make_aware(datetime(y, m, d, hh, mm))


season, _ = Season.objects.get_or_create(
    name="2026",
    defaults={
        "start_date": datetime(2026, 1, 1).date(),
        "end_date": datetime(2026, 12, 31).date(),
        "is_active": True,
    },
)

competition, _ = Competition.objects.get_or_create(
    name="Copa del Mundo 2026",
    defaults={
        "country": "Internacional",
        "level": "Selecciones absolutas",
        "competition_type": Competition.CompetitionType.INTERNATIONAL_NATIONAL,
        "organizer": "FIFA",
        "is_national_teams": True,
    },
)

federations_data = [
    {
        "name": "Real Federación Española de Fútbol",
        "short_name": "RFEF",
        "country": "España",
        "fifa_code": "ESP",
        "confederation": "UEFA",
    },
    {
        "name": "Asociación del Fútbol Argentino",
        "short_name": "AFA",
        "country": "Argentina",
        "fifa_code": "ARG",
        "confederation": "CONMEBOL",
    },
    {
        "name": "Fédération Française de Football",
        "short_name": "FFF",
        "country": "Francia",
        "fifa_code": "FRA",
        "confederation": "UEFA",
    },
]

federations = {}
for item in federations_data:
    federation, _ = Club.objects.get_or_create(
        name=item["name"],
        defaults={
            "short_name": item["short_name"],
            "entity_type": Club.EntityType.FEDERATION,
            "country": item["country"],
            "fifa_code": item["fifa_code"],
            "confederation": item["confederation"],
            "is_national_entity": True,
        },
    )

    updated = False
    for field, value in {
        "short_name": item["short_name"],
        "entity_type": Club.EntityType.FEDERATION,
        "country": item["country"],
        "fifa_code": item["fifa_code"],
        "confederation": item["confederation"],
        "is_national_entity": True,
    }.items():
        if getattr(federation, field) != value:
            setattr(federation, field, value)
            updated = True

    if updated:
        federation.save()

    federations[item["fifa_code"]] = federation


teams_data = [
    {
        "code": "ESP",
        "club": federations["ESP"],
        "name": "Selección absoluta",
        "short_name": "España",
        "team_type": Team.TeamType.NATIONAL,
        "gender": Team.Gender.MALE,
        "category": Team.Category.FIRST_TEAM,
        "country": "España",
        "fifa_ranking": 3,
        "coach_name": "Seleccionador España",
    },
    {
        "code": "ARG",
        "club": federations["ARG"],
        "name": "Selección absoluta",
        "short_name": "Argentina",
        "team_type": Team.TeamType.NATIONAL,
        "gender": Team.Gender.MALE,
        "category": Team.Category.FIRST_TEAM,
        "country": "Argentina",
        "fifa_ranking": 1,
        "coach_name": "Seleccionador Argentina",
    },
    {
        "code": "FRA",
        "club": federations["FRA"],
        "name": "Selección absoluta",
        "short_name": "Francia",
        "team_type": Team.TeamType.NATIONAL,
        "gender": Team.Gender.MALE,
        "category": Team.Category.FIRST_TEAM,
        "country": "Francia",
        "fifa_ranking": 2,
        "coach_name": "Seleccionador Francia",
    },
]

teams = {}
for item in teams_data:
    team, _ = Team.objects.get_or_create(
        club=item["club"],
        name=item["name"],
        defaults={
            "short_name": item["short_name"],
            "team_type": item["team_type"],
            "gender": item["gender"],
            "category": item["category"],
            "country": item["country"],
            "fifa_ranking": item["fifa_ranking"],
            "is_active": True,
        },
    )

    updated = False
    for field, value in {
        "short_name": item["short_name"],
        "team_type": item["team_type"],
        "gender": item["gender"],
        "category": item["category"],
        "country": item["country"],
        "fifa_ranking": item["fifa_ranking"],
        "is_active": True,
    }.items():
        if getattr(team, field) != value:
            setattr(team, field, value)
            updated = True

    if updated:
        team.save()

    TeamSeason.objects.get_or_create(
        team=team,
        season=season,
        competition=competition,
        defaults={
            "coach_name": item["coach_name"],
            "squad_label": "Convocatoria Copa del Mundo 2026",
        },
    )

    teams[item["code"]] = team


players_by_team = {
    "ESP": [
        ("Unai", "Simón", "GK"),
        ("Dani", "Carvajal", "FB"),
        ("Rodri", "Hernández", "DM"),
        ("Pedri", "González", "CM"),
        ("Álvaro", "Morata", "ST"),
    ],
    "ARG": [
        ("Emiliano", "Martínez", "GK"),
        ("Nahuel", "Molina", "FB"),
        ("Enzo", "Fernández", "CM"),
        ("Alexis", "Mac Allister", "CM"),
        ("Julián", "Álvarez", "ST"),
    ],
    "FRA": [
        ("Mike", "Maignan", "GK"),
        ("Jules", "Koundé", "FB"),
        ("Aurélien", "Tchouaméni", "DM"),
        ("Antoine", "Griezmann", "AM"),
        ("Kylian", "Mbappé", "ST"),
    ],
}

created_players = 0
created_callups = 0

for code, squad in players_by_team.items():
    national_team = teams[code]

    for idx, (first_name, last_name, position) in enumerate(squad, start=1):
        player, created = Player.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={
                "nationality": national_team.country,
                "position": position,
                "preferred_foot": "right",
                "current_team": national_team,
                "is_active": True,
            },
        )

        if created:
            created_players += 1
        else:
            updated = False
            if not player.nationality:
                player.nationality = national_team.country
                updated = True
            if not player.current_team:
                player.current_team = national_team
                updated = True
            if updated:
                player.save()

        _, was_created = NationalTeamCallUp.objects.get_or_create(
            player=player,
            team=national_team,
            competition=competition,
            start_date=datetime(2026, 6, 1).date(),
            defaults={
                "end_date": datetime(2026, 7, 20).date(),
                "squad_role": "convocado",
                "shirt_number": idx,
                "notes": "Convocatoria demo para Copa del Mundo 2026",
            },
        )
        if was_created:
            created_callups += 1


matches_data = [
    {
        "home": teams["ESP"],
        "away": teams["ARG"],
        "date": dt(2026, 6, 15, 21, 0),
        "home_score": 1,
        "away_score": 2,
        "venue": "MetLife Stadium",
        "stats": {
            "home": {
                "possession_pct": Decimal("56.00"),
                "xg": Decimal("1.420"),
                "shots": 13,
                "shots_on_target": 5,
                "passes": 610,
                "pass_accuracy_pct": Decimal("89.50"),
                "ppda": Decimal("8.70"),
                "recoveries": 52,
            },
            "away": {
                "possession_pct": Decimal("44.00"),
                "xg": Decimal("1.780"),
                "shots": 11,
                "shots_on_target": 6,
                "passes": 498,
                "pass_accuracy_pct": Decimal("84.20"),
                "ppda": Decimal("10.40"),
                "recoveries": 47,
            },
        },
    },
    {
        "home": teams["FRA"],
        "away": teams["ESP"],
        "date": dt(2026, 6, 22, 20, 0),
        "home_score": 2,
        "away_score": 2,
        "venue": "SoFi Stadium",
        "stats": {
            "home": {
                "possession_pct": Decimal("48.00"),
                "xg": Decimal("1.950"),
                "shots": 15,
                "shots_on_target": 7,
                "passes": 530,
                "pass_accuracy_pct": Decimal("86.80"),
                "ppda": Decimal("9.10"),
                "recoveries": 50,
            },
            "away": {
                "possession_pct": Decimal("52.00"),
                "xg": Decimal("1.670"),
                "shots": 12,
                "shots_on_target": 5,
                "passes": 575,
                "pass_accuracy_pct": Decimal("88.40"),
                "ppda": Decimal("8.90"),
                "recoveries": 54,
            },
        },
    },
    {
        "home": teams["ARG"],
        "away": teams["FRA"],
        "date": dt(2026, 6, 29, 21, 0),
        "home_score": 1,
        "away_score": 0,
        "venue": "AT&T Stadium",
        "stats": {
            "home": {
                "possession_pct": Decimal("46.00"),
                "xg": Decimal("1.210"),
                "shots": 10,
                "shots_on_target": 4,
                "passes": 482,
                "pass_accuracy_pct": Decimal("83.60"),
                "ppda": Decimal("10.90"),
                "recoveries": 49,
            },
            "away": {
                "possession_pct": Decimal("54.00"),
                "xg": Decimal("0.880"),
                "shots": 9,
                "shots_on_target": 2,
                "passes": 601,
                "pass_accuracy_pct": Decimal("87.30"),
                "ppda": Decimal("7.80"),
                "recoveries": 55,
            },
        },
    },
]

created_matches = 0
created_stats = 0

for item in matches_data:
    match, created = Match.objects.get_or_create(
        season=season,
        competition=competition,
        match_date=item["date"],
        home_team=item["home"],
        away_team=item["away"],
        defaults={
            "home_score": item["home_score"],
            "away_score": item["away_score"],
            "status": Match.Status.FINISHED,
            "venue": item["venue"],
        },
    )

    if created:
        created_matches += 1
    else:
        updated = False
        for field, value in {
            "home_score": item["home_score"],
            "away_score": item["away_score"],
            "status": Match.Status.FINISHED,
            "venue": item["venue"],
        }.items():
            if getattr(match, field) != value:
                setattr(match, field, value)
                updated = True
        if updated:
            match.save()

    _, stat_created = MatchTeamStat.objects.update_or_create(
        match=match,
        team=item["home"],
        defaults=item["stats"]["home"],
    )
    if stat_created:
        created_stats += 1

    _, stat_created = MatchTeamStat.objects.update_or_create(
        match=match,
        team=item["away"],
        defaults=item["stats"]["away"],
    )
    if stat_created:
        created_stats += 1

print("Seed selecciones / Copa del Mundo demo completado")
print(f"Season: {season}")
print(f"Competition: {competition}")
print(f"Federaciones: {len(federations)}")
print(f"Equipos nacionales: {len(teams)}")
print(f"Jugadores creados: {created_players}")
print(f"Convocatorias creadas: {created_callups}")
print(f"Partidos creados: {created_matches}")
print(f"MatchTeamStat creados: {created_stats}")