import datetime

import pytz
from django.db import models

from .season import Season


class WeekQuerySet(models.QuerySet):
    def for_display(self, season):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())

        return self.filter(season=season, lock_datetime__lte=right_now).order_by(
            "week_num"
        )


class Week(models.Model):
    objects = WeekQuerySet.as_manager()

    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    week_num = models.PositiveSmallIntegerField()
    lock_datetime = models.DateTimeField()

    @property
    def is_locked(self):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())
        return right_now > self.lock_datetime

    def __str__(self):
        return f"{self.week_num}"

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")
