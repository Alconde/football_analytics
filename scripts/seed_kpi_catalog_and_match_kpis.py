"""
Crea KPIType básicos y MatchKPI de ejemplo para partidos FINISHED.
Idempotente por (match, team, kpi_type).
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

django.setup()

from decimal import Decimal

from apps.kpi.models import KPIType, MatchKPI
from apps.matches.models import Match


def get_or_create_types():
    specs = [
        ("possession", "Posesión", "%", "Porcentaje de posesión"),
        ("xg", "xG", "goals", "Goles esperados acumulados"),
        ("shots", "Tiros", "count", "Tiros totales"),
        ("sot", "Tiros a puerta", "count", "Tiros entre palos"),
        ("ppda", "PPDA", "ratio", "Pases permitidos por acción defensiva"),
        ("prog_passes", "Pases progresivos", "count", "Pases que avanzan el balón"),
    ]
    types_map = {}
    for code, name, unit, desc in specs:
        kt, _ = KPIType.objects.get_or_create(
            code=code,
            defaults={"name": name, "unit": unit, "description": desc},
        )
        types_map[code] = kt
    return types_map


def seed_match_kpis_for_finished(types_map):
    created = 0
    qs = Match.objects.filter(status=Match.Status.FINISHED).select_related("home_team", "away_team")

    for m in qs:
        rows = [
            # local
            (
                m.home_team,
                {
                    "possession": Decimal("58.00"),
                    "xg": Decimal("2.10"),
                    "shots": Decimal("16"),
                    "sot": Decimal("7"),
                    "ppda": Decimal("9.50"),
                    "prog_passes": Decimal("42"),
                },
            ),
            # visitante
            (
                m.away_team,
                {
                    "possession": Decimal("42.00"),
                    "xg": Decimal("0.85"),
                    "shots": Decimal("9"),
                    "sot": Decimal("3"),
                    "ppda": Decimal("11.40"),
                    "prog_passes": Decimal("28"),
                },
            ),
        ]

        for team, bundle in rows:
            for code, val in bundle.items():
                obj, was_created = MatchKPI.objects.get_or_create(
                    match=m,
                    team=team,
                    kpi_type=types_map[code],
                    defaults={"value": val},
                )
                if was_created:
                    created += 1

    print(f"MatchKPI creados (nuevos): {created}")


def main():
    types_map = get_or_create_types()
    seed_match_kpis_for_finished(types_map)
    print("OK: catálogo KPI + MatchKPI de ejemplo.")


if __name__ == "__main__":
    main()