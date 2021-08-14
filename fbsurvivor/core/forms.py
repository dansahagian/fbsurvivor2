from django import forms

from fbsurvivor.core.models import Team, Pick


class EmailForm(forms.Form):
    email = forms.EmailField(label="email")


class SignUpCodeForm(forms.Form):
    code = forms.CharField(max_length=12)


class PickForm(forms.Form):
    def __init__(self, player, season, week, *args, **kwargs):
        super().__init__(*args, **kwargs)

        picks = Pick.objects.filter(
            player=player, week__season=season, team__isnull=False
        ).values_list("team__team_code", flat=True)

        choices = [("", "--")]
        choices.extend(
            [
                (team.team_code, team.team_code)
                for team in (
                    Team.objects.filter(season=season)
                    .exclude(bye_week=week.week_num)
                    .exclude(team_code__in=picks)
                    .order_by("team_code")
                )
            ]
        )

        self.fields["team"] = forms.ChoiceField(choices=choices, required=False)
