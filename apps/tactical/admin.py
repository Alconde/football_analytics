from django.contrib import admin
from .models import TacticalReport, TacticalPhaseObservation


@admin.register(TacticalReport)
class TacticalReportAdmin(admin.ModelAdmin):
    list_display = ("match", "team", "team_focus", "system_used", "created_by", "created_at")
    list_filter = ("team_focus", "team", "match__season")
    search_fields = ("team__name", "system_used", "strengths", "weaknesses")


@admin.register(TacticalPhaseObservation)
class TacticalPhaseObservationAdmin(admin.ModelAdmin):
    list_display = ("report", "phase", "minute_start", "minute_end", "pattern_detected", "effectiveness_score")
    list_filter = ("phase",)
    search_fields = ("pattern_detected", "notes")
