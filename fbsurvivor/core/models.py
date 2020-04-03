import datetime

import pytz
from dirtyfields import DirtyFieldsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction


class Player(models.Model):
    username = models.CharField(max_length=20, unique=True)
    link = models.CharField(max_length=44, unique=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, null=True)
    is_admin = models.BooleanField(default=False)
    is_email_confirmed = models.BooleanField(default=False)
    is_phone_confirmed = models.BooleanField(default=False)
    confirmation_code = models.IntegerField(
        null=True,
        default=None,
        validators=[MinValueValidator(111111), MaxValueValidator(999999)],
    )

    def __str__(self):
        return f"{self.username}"


class Season(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    is_locked = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year}"


class Week(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    week_num = models.PositiveSmallIntegerField()
    lock_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.week_num}"

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")


class Team(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    team_code = models.CharField(max_length=3)
    bye_week = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.team_code}"

    class Meta:
        models.UniqueConstraint(fields=["season", "team_code"], name="unique_team")


class Pick(DirtyFieldsMixin, models.Model):
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
            current_value = result["current"]

            if current_value == "W":
                ps.win_count += 1

            if current_value == "L":
                ps.loss_count += 1

            if saved_value == "W":
                ps.win_count += -1

            if saved_value == "L":
                ps.loss_count += -1

            with transaction.atomic():
                ps.save()
                super().save(*args, **kwargs)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")


class PlayerStatus(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    is_paid = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_survivor = models.BooleanField(default=True)
    win_count = models.SmallIntegerField(default=0)
    loss_count = models.SmallIntegerField(default=0)

    def get_picks(self):
        right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())

        return Pick.objects.filter(
            player=self.player,
            week__season=self.season,
            week__lock_datetime__lte=right_now,
        )

    def __str__(self):
        return f"{self.player} - {self.season}"

    class Meta:
        models.UniqueConstraint(fields=["player", "season"], name="unique_playerstatus")
        verbose_name_plural = "playerstatuses"
