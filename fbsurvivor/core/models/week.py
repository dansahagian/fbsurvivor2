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

    def get_current(self, season):
        qs = self.for_display(season)
        return qs.last() if qs else None

    def get_next(self, season):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())
        qs = self.filter(season=season, lock_datetime__gt=right_now).order_by(
            "week_num"
        )
        return qs.first() if qs else None


class Week(models.Model):
    objects = WeekQuerySet.as_manager()

    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    week_num = models.PositiveSmallIntegerField()
    lock_datetime = models.DateTimeField(null=True)

    @property
    def is_locked(self):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())
        return right_now > self.lock_datetime if self.lock_datetime else False

    def __str__(self):
        return f"{self.week_num}"

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")
