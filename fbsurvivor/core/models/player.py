from django.db import models
from django.db.models import Sum
from django.db.models.functions import Lower

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task
from .season import Season


class Player(models.Model):
    username = models.CharField(max_length=20, unique=True)
    link = models.CharField(max_length=44, unique=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    has_email_reminders = models.BooleanField(default=True)
    has_phone_reminders = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        indexes = [models.Index(fields=["link"])]

    def save(self, *args, **kwargs):
        pk = self.pk
        super().save(*args, **kwargs)

        if not pk and not settings.DEBUG:
            ps = f"If you didn't sign up, please email {settings.CONTACT}"
            link = f"{settings.DOMAIN}/board/{self.link}/"
            subject = "Survivor User Account"
            recipients = [self.email]
            message = f"You can use this link to manage your account:\n\n{link}\n\n{ps}"

            send_email_task.delay(subject, recipients, message)


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
            .order_by("-is_survivor", "-win_count", "loss_count", "is_retired", "lower")
        )

    def paid_for_season(self, season):
        return (
            self.filter(season=season)
            .annotate(lower=Lower("player__username"))
            .order_by("-is_paid", "lower")
        )

    def for_reminders(self, week):
        return self.filter(
            season=week.season,
            is_retired=False,
            player__pick__week=week,
            player__pick__team__isnull=True,
        )

    def for_email_reminders(self, week):
        return (
            self.for_reminders(week)
            .filter(player__has_email_reminders=True)
            .values_list("player__email", flat=True)
        )

    def for_phone_reminders(self, week):
        return (
            self.for_reminders(week)
            .filter(player__has_phone_reminders=True, player__phone__isnull=False)
            .values_list("player__phone", flat=True)
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


class PayoutQuerySet(models.QuerySet):
    def for_payout_table(self):
        return (
            self.values("player")
            .annotate(total=Sum("amount"))
            .order_by("-total")
            .values("player__username", "total", "player__notes")
        )


class Payout(models.Model):
    objects = PayoutQuerySet.as_manager()

    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.player} - {self.season} - {self.amount}"

    class Meta:
        models.UniqueConstraint(fields=["player", "season"], name="unique_payout")
        verbose_name_plural = "payouts"
