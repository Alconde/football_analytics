from django.contrib import admin
from .models import WellnessReport, GPSLoad


@admin.register(WellnessReport)
class WellnessReportAdmin(admin.ModelAdmin):
    list_display = ("player", "report_date", "fatigue", "soreness", "stress", "sleep_quality", "rpe")
    list_filter = ("report_date",)
    search_fields = ("player__first_name", "player__last_name")


@admin.register(GPSLoad)
class GPSLoadAdmin(admin.ModelAdmin):
    list_display = ("player", "session_date", "match", "total_distance_m", "high_speed_distance_m", "sprint_count")
    list_filter = ("session_date",)
    search_fields = ("player__first_name", "player__last_name")
