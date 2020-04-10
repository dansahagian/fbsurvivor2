import datetime

import pytz
from dirtyfields import DirtyFieldsMixin
from django.db import models

from .player import Player
from .team import Team
from .week import Week


class PickQuerySet(models.QuerySet):
    def for_player_season(self, player, season):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())

        return self.filter(
            player=player, week__season=season, week__lock_datetime__lte=right_now,
        ).order_by("week__week_num")


class Pick(DirtyFieldsMixin, models.Model):
    objects = PickQuerySet.as_manager()

    result_choices = [
        ("W", "WIN"),
        ("L", "LOSS"),
        ("R", "RETIRED"),
    ]
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True)
    result = models.CharField(
        choices=result_choices, max_length=1, null=True, blank=True
    )

    FIELDS_TO_CHECK = ["result"]

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")
