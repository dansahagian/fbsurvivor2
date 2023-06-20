from django import forms

from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.team import Team


class EmailForm(forms.Form):
    email = forms.EmailField(label="email")


class PlayerForm(forms.Form):
    username = forms.CharField(label="username", max_length=20)
    email = forms.EmailField(label="email (won't be displayed)")
    league = forms.CharField(label="league", max_length=12)


class PickForm(forms.Form):
    def __init__(self, player, season, week, *args, **kwargs):
        super().__init__(*args, **kwargs)

        picks = Pick.objects.filter(
            player=player, week__season=season, team__isnull=False
        ).values_list("team__team_code", flat=True)

        choices = [("", "--")]
        choices.extend(
            [
                (team.team_code, f"{team.team_code} ({team.name})")
                for team in (
                    Team.objects.filter(season=season)
                    .exclude(bye_week=week.week_num)
                    .exclude(team_code__in=picks)
                    .order_by("team_code")
                )
                if not team.is_locked(week)
            ]
        )

        self.fields["team"] = forms.ChoiceField(choices=choices, required=False)


class MessageForm(forms.Form):
    subject = forms.CharField(label="subject", max_length=25)
    message = forms.CharField(label="message", widget=forms.Textarea)


class RemindersForm(forms.Form):
    def __init__(self, player, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["has_email_reminders"] = forms.BooleanField()
        self.fields["has_push_reminders"] = forms.BooleanField()

        self.fields["has_email_reminders"].initial = player.has_email_reminders
        self.fields["has_push_reminders"].initial = player.has_push_reminders
