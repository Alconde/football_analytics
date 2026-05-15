from django.contrib import admin
from .models import KPIType, MatchKPI, PlayerKPI


@admin.register(KPIType)
class KPITypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "unit")
    search_fields = ("code", "name")


@admin.register(MatchKPI)
class MatchKPIAdmin(admin.ModelAdmin):
    list_display = ("match", "team", "kpi_type", "value")
    list_filter = ("kpi_type", "team")
    search_fields = ("team__name", "kpi_type__code")


@admin.register(PlayerKPI)
class PlayerKPIAdmin(admin.ModelAdmin):
    list_display = ("match", "player", "kpi_type", "value")
    list_filter = ("kpi_type",)
    search_fields = ("player__first_name", "player__last_name", "kpi_type__code")
