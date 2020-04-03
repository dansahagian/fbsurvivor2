import datetime

import pytz
from dirtyfields import DirtyFieldsMixin
from django.db import models, transaction

from .player import Player
from .playerstatus import PlayerStatus
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
    result = models.CharField(choices=result_choices, max_length=1, null=True)

    FIELDS_TO_CHECK = ["result"]

    def save(self, *args, **kwargs):
        if not self._state.adding and self.is_dirty():
            ps = PlayerStatus.objects.get(player=self.player, season=self.week.season,)
            result = self.get_dirty_fields(verbose=True)["result"]
            saved_value = result["saved"]
            dirty_value = result["current"]

            ps.win_count = ps.win_count + 1 if dirty_value == "W" else ps.win_count
            ps.win_count = ps.win_count - 1 if saved_value == "W" else ps.win_count

            ps.loss_count = ps.loss_count + 1 if dirty_value == "L" else ps.loss_count
            ps.loss_count = ps.loss_count - 1 if saved_value == "L" else ps.loss_count

            with transaction.atomic():
                ps.save()
                super().save(*args, **kwargs)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")
