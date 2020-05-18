from django.db import models

from fbsurvivor.core.utils import get_localized_right_now
from .player import Player
from .team import Team
from .week import Week


class PickQuerySet(models.QuerySet):
    def for_player_season(self, player, season):
        return self.filter(player=player, week__season=season).order_by(
            "week__week_num"
        )

    def for_player_season_locked(self, player, season):
        return self.for_player_season(player, season).filter(
            week__lock_datetime__lte=get_localized_right_now(),
        )

    def for_results(self, week):
        return (
            self.filter(week=week, result__isnull=True, team__isnull=False)
            .values_list("team__team_code", flat=True)
            .distinct()
        )

    def for_result_updates(self, week, team):
        return self.filter(week=week, team=team, result__isnull=True)

    def for_no_picks(self, week):
        return self.filter(week=week, team__isnull=True, result__isnull=True)


class Pick(models.Model):
    objects = PickQuerySet.as_manager()

    result_choices = [
        ("W", "WIN"),
        ("L", "LOSS"),
        ("R", "RETIRED"),
    ]
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True)
    result = models.CharField(choices=result_choices, max_length=1, null=True)

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")
