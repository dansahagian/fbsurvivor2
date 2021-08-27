import arrow
from django.db import models

from .season import Season


class WeekQuerySet(models.QuerySet):
    def for_display(self, season):
        return self.filter(
            season=season, lock_datetime__lte=arrow.now().datetime
        ).order_by("week_num")

    def get_current(self, season):
        qs = self.for_display(season)
        return qs.last() if qs else None

    def get_next(self, season):
        qs = self.filter(
            season=season, lock_datetime__gt=arrow.now().datetime
        ).order_by("week_num")
        return qs.first() if qs else None


class Week(models.Model):
    objects = WeekQuerySet.as_manager()

    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    week_num = models.PositiveSmallIntegerField()
    lock_datetime = models.DateTimeField(null=True)

    @property
    def is_locked(self):
        return arrow.now() > self.lock_datetime if self.lock_datetime else False

    def __str__(self):
        return f"{self.season} | {self.week_num}"

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")
