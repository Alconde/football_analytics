"""
Crea KPIType básicos y MatchKPI de ejemplo para partidos FINISHED.
Idempotente por (match, team, kpi_type).
"""

from decimal import Decimal

from apps.kpi.models import KPIType, MatchKPI
from apps.matches.models import Match


def get_or_create_types():
    """
    Crea el catálogo básico de KPIType si no existe y devuelve
    un mapa code -> KPIType.
    """
    specs = [
        ("possession", "Posesión", "%", "Porcentaje de posesión"),
        ("xg", "xG", "goals", "Goles esperados acumulados"),
        ("shots", "Tiros", "count", "Tiros totales"),
        ("sot", "Tiros a puerta", "count", "Tiros entre palos"),
        ("ppda", "PPDA", "ratio", "Pases permitidos por acción defensiva"),
        ("prog_passes", "Pases progresivos", "count", "Pases que avanzan el balón"),
    ]
    types_map = {}
    created = 0

    for code, name, unit, desc in specs:
        kt, was_created = KPIType.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "unit": unit,
                "description": desc,
            },
        )
        types_map[code] = kt
        if was_created:
            created += 1

    print(f"✅ KPIType preparados. Nuevos creados: {created}")
    return types_map


def seed_match_kpis_for_finished(types_map: dict[str, KPIType]):
    """
    Crea o actualiza KPIs de ejemplo para todos los partidos FINISHED.
    Usa update_or_create para ser idempotente.
    """
    matches = (
        Match.objects.filter(status=Match.Status.FINISHED)
        .select_related("home_team", "away_team")
    )

    if not matches.exists():
        print("⚠️ No hay partidos finalizados para asignar KPIs.")
        return

    created = 0
    updated = 0

    for m in matches:
        rows = [
            # Local
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
            # Visitante
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
                obj, was_created = MatchKPI.objects.update_or_create(
                    match=m,
                    team=team,
                    kpi_type=types_map[code],
                    defaults={"value": val},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

    print(f"✅ MatchKPI procesados. Creados: {created}, actualizados: {updated}")


def run():
    """
    Punto de entrada estándar para ejecutar el seed desde manage.py shell.
    """
    types_map = get_or_create_types()
    seed_match_kpis_for_finished(types_map)
    print("OK: catálogo KPI + MatchKPI de ejemplo.")