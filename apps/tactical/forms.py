from django import forms

from .models import TacticalReport


class TacticalReportForm(forms.ModelForm):
    class Meta:
        model = TacticalReport
        fields = [
            "match",
            "team",
            "team_focus",
            "system_used",
            "strengths",
            "weaknesses",
            "recurring_errors",
            "coach_notes",
        ]