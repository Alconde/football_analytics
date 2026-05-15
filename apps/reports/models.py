from django.db import models
from django.conf import settings

from apps.matches.models import Match
from apps.players.models import Player
from apps.clubs.models import Team


class GeneratedReport(models.Model):
    class ReportType(models.TextChoices):
        OPPONENT = "opponent", "Informe de rival"
        POSTMATCH = "postmatch", "Informe postpartido"
        INDIVIDUAL = "individual", "Informe individual"
        TACTICAL = "tactical", "Informe táctico"
        EXECUTIVE = "executive", "Resumen ejecutivo"

    class FileType(models.TextChoices):
        PDF = "pdf", "PDF"
        PPTX = "pptx", "PowerPoint"
        XLSX = "xlsx", "Excel"

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    file_type = models.CharField(max_length=10, choices=FileType.choices, default=FileType.PDF)

    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="generated_reports"
    )
    file = models.FileField(upload_to="reports/")
    summary = models.TextField(blank=True)

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return self.title
