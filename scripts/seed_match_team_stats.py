# scripts/seed_matchteamstats.py
import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.matches.models import Match, MatchTeamStat  # noqa


def main():
    partidos = list(
        Match.objects.filter(status=Match.Status.FINISHED)
        .select_related("home_team", "away_team")
        .order_by("match_date")
    )

    if not partidos:
        print("No hay partidos finalizados. Crea alguno primero.")
        return

    # Tres perfiles de partido de ejemplo
    perfiles = [
        # Partido 1: dominio ligero del local
        dict(
            home=dict(
                possessionpct=Decimal("54.2"),
                xg=Decimal("1.35"),
                shots=14,
                shotsontarget=6,
                passes=420,
                passaccuracypct=Decimal("82.5"),
                ppda=Decimal("9.8"),
                recoveries=58,
            ),
            away=dict(
                possessionpct=Decimal("45.8"),
                xg=Decimal("0.92"),
                shots=10,
                shotsontarget=3,
                passes=350,
                passaccuracypct=Decimal("79.1"),
                ppda=Decimal("11.4"),
                recoveries=49,
            ),
        ),
        # Partido 2: visitante más eficiente
        dict(
            home=dict(
                possessionpct=Decimal("52.0"),
                xg=Decimal("0.87"),
                shots=11,
                shotsontarget=3,
                passes=378,
                passaccuracypct=Decimal("78.9"),
                ppda=Decimal("9.1"),
                recoveries=52,
            ),
            away=dict(
                possessionpct=Decimal("48.0"),
                xg=Decimal("1.45"),
                shots=10,
                shotsontarget=5,
                passes=342,
                passaccuracypct=Decimal("83.2"),
                ppda=Decimal("7.8"),
                recoveries=49,
            ),
        ),
        # Partido 3: partido muy igualado
        dict(
            home=dict(
                possessionpct=Decimal("55.2"),
                xg=Decimal("1.53"),
                shots=13,
                shotsontarget=5,
                passes=395,
                passaccuracypct=Decimal("80.1"),
                ppda=Decimal("8.7"),
                recoveries=50,
            ),
            away=dict(
                possessionpct=Decimal("44.8"),
                xg=Decimal("1.21"),
                shots=8,
                shotsontarget=4,
                passes=315,
                passaccuracypct=Decimal("77.4"),
                ppda=Decimal("9.8"),
                recoveries=54,
            ),
        ),
    ]

    creados = 0
    for idx, match in enumerate(partidos):
        perfil = perfiles[min(idx, len(perfiles) - 1)]

        for side in ("home", "away"):
            team = match.home_team if side == "home" else match.away_team
            stats_defaults = perfil[side]

            obj, created = MatchTeamStat.objects.get_or_create(
                match=match,
                team=team,
                defaults=stats_defaults,
            )
            if created:
                creados += 1

    print(f"MatchTeamStat creados nuevos: {creados}")


if __name__ == "__main__":
    main()