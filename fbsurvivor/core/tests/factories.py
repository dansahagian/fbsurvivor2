import factory

from fbsurvivor.core import models
from fbsurvivor.core.utils import get_localized_right_now


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Player

    username = factory.Sequence(lambda n: f"Player{n + 1}")
    link = factory.Sequence(lambda n: f"secretlink{n + 1}")
    email = factory.LazyAttribute(lambda a: f"{a.username}@fbsurvivor.com")


class SeasonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Season

    year = factory.Sequence(lambda n: n + 2017)
    is_locked = True
    is_current = False


class WeekFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Week

    season = factory.SubFactory(SeasonFactory)
    week_num = factory.Sequence(lambda n: n + 1)
    lock_datetime = get_localized_right_now()


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Team

    season = factory.SubFactory(SeasonFactory)
    team_code = factory.Sequence(lambda n: f"T{n + 1}")
    bye_week = factory.Sequence(lambda n: n + 1)


class PickFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Pick

    player = factory.SubFactory(PlayerFactory)
    week = factory.SubFactory(WeekFactory)
    team = factory.SubFactory(TeamFactory)


class PlayerStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PlayerStatus

    player = factory.SubFactory(PlayerFactory)
    season = factory.SubFactory(SeasonFactory)
