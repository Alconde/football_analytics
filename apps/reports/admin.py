from django.contrib import admin
from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "file_type", "match", "team", "player", "generated_by", "generated_at")
    list_filter = ("report_type", "file_type", "generated_at")
    search_fields = ("title", "summary")
