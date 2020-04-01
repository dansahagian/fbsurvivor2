from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=20, unique=True)
    link = models.CharField(max_length=44, unique=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, null=True)
    is_admin = models.BooleanField(default=False)
    is_email_confirmed = models.BooleanField(default=False)
    is_phone_confirmed = models.BooleanField(default=False)

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

    class Meta:
        models.UniqueConstraint(fields=["season", "week_num"], name="unique_week")

    def __str__(self):
        return f"{self.week_num} - {self.season}"


class PlayerStatus(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    is_paid = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_survivor = models.BooleanField(default=True)

    class Meta:
        models.UniqueConstraint(fields=["player", "season"], name="unique_playerstatus")

    def __str__(self):
        return f"{self.player} - {self.season}"


class Team(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    team_code = models.CharField(max_length=3)
    bye_week = models.PositiveSmallIntegerField()

    class Meta:
        models.UniqueConstraint(fields=["season", "team_code"], name="unique_team")

    def __str__(self):
        return f"{self.team_code} - {self.season}"


class Pick(models.Model):
    result_choices = [
        ("W", "WIN"),
        ("L", "LOSS"),
        ("R", "RETIRED"),
    ]
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True)
    result = models.CharField(choices=result_choices, max_length=1, null=True)

    class Meta:
        models.UniqueConstraint(fields=["player", "week"], name="unique_pick")

    def __str__(self):
        return f"{self.player} - {self.week} - {self.team}"
