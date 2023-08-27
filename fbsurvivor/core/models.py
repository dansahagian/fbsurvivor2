import arrow
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Lower

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task


class League(models.Model):
    code = models.CharField(max_length=12)
    name = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Player(models.Model):
    username = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, blank=True, default="")

    league = models.ForeignKey(League, null=True, on_delete=models.DO_NOTHING)

    emoji = models.CharField(max_length=8, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    is_admin = models.BooleanField(default=False)
    is_dark_mode = models.BooleanField(default=False)

    has_email_reminders = models.BooleanField(default=True)
    has_sms_reminders = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["username"]), models.Index(fields=["email"])]

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        pk = self.pk
        super().save(*args, **kwargs)

        if not pk:
            ps = f"If you didn't sign up, please email {settings.CONTACT}"
            signin = f"{settings.DOMAIN}"
            subject = "Survivor User Account"
            recipients = [self.email]
            message = f"You can login here:\n\n{signin}\n\n{ps}"

            send_email_task.delay(subject, recipients, message)


class TokenHash(models.Model):
    hash = models.CharField(max_length=128)
    player = models.ForeignKey(
        Player, related_name="tokens", related_query_name="token", on_delete=models.CASCADE
    )
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["hash"])]


class Season(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    is_locked = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year}"

    class Meta:
        ordering = ["-year"]
        indexes = [models.Index(fields=["year"])]


class PlayerStatusQuerySet(models.QuerySet):
    def player_years(self, player):
        return (
            self.filter(player=player)
            .values_list("season__year", flat=True)
            .order_by("-season__year")
        )

    def for_season_board(self, season, league):
        return (
            self.filter(season=season, player__league=league)
            .annotate(lower=Lower("player__username"))
            .order_by("-is_survivor", "is_retired", "-win_count", "loss_count", "lower")
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

    def for_sms_reminders(self, week):
        return (
            self.for_reminders(week)
            .filter(player__has_sms_reminders=True)
            .values_list("player__phone_number", flat=True)
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
    def for_payout_table(self, league):
        return (
            self.filter(player__league=league)
            .values("player")
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


class WeekQuerySet(models.QuerySet):
    def for_display(self, season):
        return self.filter(season=season, lock_datetime__lte=arrow.now().datetime).order_by(
            "week_num"
        )

    def get_current(self, season):
        qs = self.for_display(season)
        return qs.last() if qs else None

    def get_next(self, season):
        qs = self.filter(season=season, lock_datetime__gt=arrow.now().datetime).order_by(
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
        return arrow.now() > self.lock_datetime if self.lock_datetime else False

    def __str__(self):
        return f"{self.season} | {self.week_num}"

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")


class Team(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    team_code = models.CharField(max_length=3)
    name = models.CharField(max_length=15, default="")
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


class Lock(models.Model):
    week = models.ForeignKey("core.Week", on_delete=models.CASCADE)
    team = models.ForeignKey("core.Team", on_delete=models.CASCADE)
    lock_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.week} | {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["week", "team"], name="unique_lock")


class PickQuerySet(models.QuerySet):
    def for_player_season(self, player, season):
        return self.filter(player=player, week__season=season).order_by("week__week_num")

    def for_board(self, player, season):
        return (
            self.for_player_season(player, season)
            .order_by("-week__week_num")
            .filter(
                week__lock_datetime__lte=arrow.now().datetime,
            )
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
    result = models.CharField(choices=result_choices, max_length=1, null=True, blank=True)

    @property
    def is_locked(self):
        try:
            lock = Lock.objects.get(week=self.week, team=self.team)
            return arrow.now() > lock.lock_datetime if lock.lock_datetime else False
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
