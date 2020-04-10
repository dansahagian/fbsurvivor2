from django.db import models

from .pick import Pick
from .player import Player
from .season import Season


class PlayerStatus(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    is_paid = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_survivor = models.BooleanField(default=True)
    win_count = models.SmallIntegerField(default=0)
    loss_count = models.SmallIntegerField(default=0)

    def update_record(self):
        picks = Pick.objects.filter(player=self.player, week__season=self.season)
        self.win_count = picks.filter(result="W").count()
        self.loss_count = picks.filter(result="L").count()
        self.save()
        return True

    def __str__(self):
        return f"{self.player} - {self.season}"

    class Meta:
        models.UniqueConstraint(fields=["player", "season"], name="unique_playerstatus")
        verbose_name_plural = "playerstatuses"
