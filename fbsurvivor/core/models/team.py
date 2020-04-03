from django.db import models

from .season import Season


class Team(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    team_code = models.CharField(max_length=3)
    bye_week = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.team_code}"

    class Meta:
        models.UniqueConstraint(fields=["season", "team_code"], name="unique_team")
