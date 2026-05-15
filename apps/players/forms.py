from django import forms

from apps.clubs.models import Team
from .models import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "nationality",
            "preferred_foot",
            "position",
            "height_cm",
            "weight_kg",
            "current_team",
            "is_active",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["current_team"].queryset = Team.objects.select_related("club").order_by("club__name", "name")