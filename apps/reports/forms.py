from django import forms
from apps.matches.models import Match
from apps.players.models import Player
from apps.clubs.models import Team
from .models import GeneratedReport


class GeneratedReportForm(forms.ModelForm):
    match = forms.ModelChoiceField(
        queryset=Match.objects.filter(status=Match.Status.FINISHED).order_by("-match_date"),
        required=False,
        label="Partido",
        help_text="Selecciona un partido para generar el informe postpartido.",
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.filter(is_active=True).order_by("club__name", "name"),
        required=False,
        label="Equipo",
        help_text="Opcional: selecciona el equipo principal del informe.",
    )
    player = forms.ModelChoiceField(
        queryset=Player.objects.filter(is_active=True).order_by("last_name", "first_name"),
        required=False,
        label="Jugador",
        help_text="Opcional: selecciona un jugador para análisis individual.",
    )

    class Meta:
        model = GeneratedReport
        fields = ["title", "report_type", "file_type", "match", "team", "player"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Título del informe"}),
            "report_type": forms.Select(attrs={"class": "border-slate-700 bg-slate-950"}),
            "file_type": forms.Select(attrs={"class": "border-slate-700 bg-slate-950"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        match = cleaned_data.get("match")
        team = cleaned_data.get("team")
        player = cleaned_data.get("player")

        if not any([match, team, player]):
            raise forms.ValidationError(
                "Debes seleccionar al menos un partido, equipo o jugador para generar el informe."
            )

        if cleaned_data.get("title") is None:
            cleaned_data["title"] = self.fields["report_type"].label

        return cleaned_data
