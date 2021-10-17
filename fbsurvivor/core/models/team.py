import arrow
from django.db import models

from .lock import Lock
from .season import Season
from .week import Week


class Team(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    team_code = models.CharField(max_length=3)
    bye_week = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.season} | {self.team_code}"

    class Meta:
        models.UniqueConstraint(fields=["season", "team_code"], name="unique_team")
        ordering = ["-season", "team_code"]

    def is_locked(self, week: Week) -> bool:
        try:
            lock = Lock.objects.get(week=week, team=self)
            return arrow.now() > lock.lock_datetime if lock.lock_datetime else False
        except Lock.DoesNotExist:
            return week.is_locked
