from decimal import Decimal

import django

django.setup()

from apps.matches.models import Match, MatchTeamStat


def main():
    qs = Match.objects.filter(status=Match.Status.FINISHED).select_related("home_team", "away_team")
    created = 0
    for m in qs:
        for team, poss, xg, shots, sot, ppda, rec in (
            (
                m.home_team,
                Decimal("54.20"),
                Decimal("1.350"),
                14,
                6,
                Decimal("9.80"),
                58,
            ),
            (
                m.away_team,
                Decimal("45.80"),
                Decimal("0.920"),
                10,
                3,
                Decimal("11.40"),
                49,
            ),
        ):
            obj, was_created = MatchTeamStat.objects.get_or_create(
                match=m,
                team=team,
                defaults={
                    "possession_pct": poss,
                    "xg": xg,
                    "shots": shots,
                    "shots_on_target": sot,
                    "passes": 420,
                    "pass_accuracy_pct": Decimal("82.50"),
                    "ppda": ppda,
                    "recoveries": rec,
                },
            )
            if was_created:
                created += 1
    print(f"MatchTeamStat creados (nuevos): {created}")


if __name__ == "__main__":
    main()