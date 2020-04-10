import datetime

import factory
import pytest
import pytz

from fbsurvivor.core.models import Pick
from fbsurvivor.core.tests.factories import (
    PlayerFactory,
    SeasonFactory,
    WeekFactory,
    PickFactory,
)

PST = pytz.timezone("US/Pacific")


@pytest.fixture
def players(db):
    return PlayerFactory.create_batch(size=2)


@pytest.fixture
def season(db):
    return SeasonFactory()


@pytest.fixture
def weeks(db, season):
    now = PST.localize(datetime.datetime.now())
    nw = now + datetime.timedelta(days=7)
    lw = now - datetime.timedelta(days=7)

    return WeekFactory.create_batch(
        size=5, season=season, lock_datetime=factory.Iterator([lw, lw, lw, lw, nw])
    )


@pytest.fixture
def picks(db, players, weeks):
    picks = [
        PickFactory.create_batch(
            size=5, player=players[0], week=factory.Iterator(weeks)
        ),
        PickFactory.create_batch(
            size=5, player=players[1], week=factory.Iterator(weeks)
        ),
    ]

    return picks


def test_pick_for_player_season(db, players, season, picks):
    queryset = Pick.objects.for_player_season(players[0], season)
    assert queryset.count() == 4
    assert list(queryset) == picks[0][:4]


def test_pick_for_result(db, weeks, picks):
    queryset = Pick.objects.for_results(weeks[1])
    assert queryset.count() == 2
