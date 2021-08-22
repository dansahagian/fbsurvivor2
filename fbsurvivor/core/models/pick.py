import datetime

import pytz
from django.db import models

from .lock import Lock
from .player import Player
from .team import Team
from .week import Week


class PickQuerySet(models.QuerySet):
    def for_player_season(self, player, season):
        return self.filter(player=player, week__season=season).order_by(
            "week__week_num"
        )

    def for_board(self, player, season):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())

        return self.for_player_season(player, season).filter(
            week__lock_datetime__lte=right_now,
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
        (None, "None"),
    ]
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True)
    result = models.CharField(
        choices=result_choices, max_length=1, null=True, blank=True
    )

    @property
    def is_locked(self):
        try:
            lock = Lock.objects.get(week=self.week, team=self.team)
            right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())
            return right_now > lock.lock_datetime if lock.lock_datetime else False
        except Lock.DoesNotExist:
            return self.week.is_locked

    @property
    def deadline(self):
        try:
            lock = Lock.objects.get(week=self.week, team=self.team)
            return lock.lock_datetime
        except Lock.DoesNotExist:
            return self.week.lock_datetime

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")
        indexes = [models.Index(fields=["player", "week"])]
