from decimal import Decimal
from apps.matches.models import Match, MatchTeamStat

partidos_finalizados = Match.objects.filter(
    status=Match.Status.FINISHED
).select_related("home_team", "away_team").order_by("match_date")

if not partidos_finalizados.exists():
    print("No hay partidos finalizados.")
else:
    creados = 0
    actualizados = 0

    for i, match in enumerate(partidos_finalizados, start=1):
        home_defaults = {
            "possession_pct": Decimal(str(52 + (i % 7))),
            "xg": Decimal(str(round(1.10 + (i * 0.17), 2))),
            "shots": 10 + i,
            "shots_on_target": 3 + (i % 4),
            "passes": 320 + (i * 18),
            "pass_accuracy_pct": Decimal(str(round(77.5 + (i % 6), 2))),
            "ppda": Decimal(str(round(8.0 + (i % 3) * 0.7, 2))),
            "recoveries": 44 + i,
        }

        away_defaults = {
            "possession_pct": Decimal(str(max(35, 48 - (i % 7)))),
            "xg": Decimal(str(round(0.85 + (i * 0.13), 2))),
            "shots": 8 + i,
            "shots_on_target": 2 + (i % 3),
            "passes": 280 + (i * 15),
            "pass_accuracy_pct": Decimal(str(round(74.5 + (i % 5), 2))),
            "ppda": Decimal(str(round(9.1 + (i % 4) * 0.6, 2))),
            "recoveries": 46 + i,
        }

        _, created = MatchTeamStat.objects.update_or_create(
            match=match,
            team=match.home_team,
            defaults=home_defaults,
        )
        if created:
            creados += 1
        else:
            actualizados += 1

        _, created = MatchTeamStat.objects.update_or_create(
            match=match,
            team=match.away_team,
            defaults=away_defaults,
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    print(f"MatchTeamStat procesados correctamente. Creados: {creados}, actualizados: {actualizados}")