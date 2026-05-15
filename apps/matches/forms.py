from django import forms
from django.core.exceptions import ValidationError

from apps.clubs.models import Competition, Season, Team
from .models import Match


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            "season",
            "competition",
            "match_date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "status",
            "venue",
        ]
        widgets = {
            "match_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "season": forms.Select(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "competition": forms.Select(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "home_team": forms.Select(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "away_team": forms.Select(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "home_score": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "away_score": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
            "venue": forms.TextInput(
                attrs={
                    "class": "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["season"].queryset = Season.objects.order_by("-start_date")
        self.fields["competition"].queryset = Competition.objects.order_by("name")
        self.fields["home_team"].queryset = Team.objects.select_related("club").order_by("club__name", "name")
        self.fields["away_team"].queryset = Team.objects.select_related("club").order_by("club__name", "name")

        if self.instance and self.instance.pk and self.instance.match_date:
            self.initial["match_date"] = self.instance.match_date.strftime("%Y-%m-%dT%H:%M")

    def clean(self):
        cleaned_data = super().clean()

        home_team = cleaned_data.get("home_team")
        away_team = cleaned_data.get("away_team")
        home_score = cleaned_data.get("home_score")
        away_score = cleaned_data.get("away_score")
        status = cleaned_data.get("status")

        if home_team and away_team and home_team == away_team:
            raise ValidationError("El equipo local y el visitante no pueden ser el mismo.")

        if status == Match.Status.FINISHED:
            if home_score is None or away_score is None:
                raise ValidationError("Si el partido está finalizado, debes indicar ambos marcadores.")

        if status != Match.Status.FINISHED:
            if home_score is not None or away_score is not None:
                raise ValidationError(
                    "Solo debes informar el marcador cuando el partido esté finalizado."
                )

        return cleaned_data