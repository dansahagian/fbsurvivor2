from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.functions import Lower

from .season import Season


class PlayerQuerySet(models.QuerySet):
    def for_reminders(self, week):
        return self.filter(pick__week=week, pick__team__isnull=True)

    def for_email_reminders(self, week):
        return (
            self.for_reminders(week)
            .filter(has_email_reminders=True)
            .values_list("email", flat=True)
        )

    def for_phone_reminders(self, week):
        return (
            self.for_reminders(week)
            .filter(has_phone_reminders=True, phone__isnull=False)
            .values_list("phone", flat=True)
        )


class Player(models.Model):
    objects = PlayerQuerySet.as_manager()

    username = models.CharField(max_length=20, unique=True)
    link = models.CharField(max_length=44, unique=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, null=True)
    is_admin = models.BooleanField(default=False)
    has_email_reminders = models.BooleanField(default=False)
    has_phone_reminders = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        indexes = [models.Index(fields=["link"])]


class PlayerStatusQuerySet(models.QuerySet):
    def player_years(self, player):
        return (
            self.filter(player=player)
            .values_list("season__year", flat=True)
            .order_by("-season__year")
        )

    def for_season_board(self, season):
        return (
            self.filter(season=season)
            .annotate(lower=Lower("player__username"))
            .order_by("-is_survivor", "is_retired", "-win_count", "loss_count", "lower")
        )

    def paid_for_season(self, season):
        return (
            self.filter(season=season)
            .annotate(lower=Lower("player__username"))
            .order_by("-is_paid", "lower")
        )


class PlayerStatus(models.Model):
    objects = PlayerStatusQuerySet.as_manager()

    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    is_paid = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_survivor = models.BooleanField(default=True)
    win_count = models.SmallIntegerField(default=0)
    loss_count = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.season}"

    class Meta:
        models.UniqueConstraint(fields=["player", "season"], name="unique_playerstatus")
        verbose_name_plural = "playerstatuses"
        indexes = [models.Index(fields=["player", "season"])]
