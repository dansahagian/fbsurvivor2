import datetime

import factory
import pytest
import pytz


from fbsurvivor.core.tests.factories import (
    PlayerFactory,
    PlayerStatusFactory,
    SeasonFactory,
    WeekFactory,
    PickFactory,
    TeamFactory,
)


PST = pytz.timezone("US/Pacific")


@pytest.fixture(autouse=True)
def players(db):
    return PlayerFactory.create_batch(
        size=2,
        username=factory.Iterator(["Automator", "Roboto"]),
        link=factory.Iterator(["ABC123", "DEF456"]),
    )


@pytest.fixture(autouse=True)
def seasons(db):
    return SeasonFactory.create_batch(
        size=2,
        year=factory.Iterator([2019, 2020]),
        is_locked=factory.Iterator([True, False]),
        is_current=factory.Iterator([False, True]),
    )


@pytest.fixture(autouse=True)
def weeks(db, seasons):
    now = PST.localize(datetime.datetime.now())
    nw = now + datetime.timedelta(days=7)
    lw = now - datetime.timedelta(days=7)

    return WeekFactory.create_batch(
        size=5,
        season=seasons[1],
        week_num=factory.Iterator([1, 2, 3, 4, 5]),
        lock_datetime=factory.Iterator([lw, lw, lw, lw, nw]),
    )


@pytest.fixture(autouse=True)
def teams(db, seasons):
    return (
        TeamFactory.create_batch(
            size=5,
            season=seasons[1],
            team_code=factory.Iterator(["NE", "SF", "TB", "GB", "DAL"]),
            bye_week=factory.Iterator([1, 2, 3, 4, 5]),
        )
    )


@pytest.fixture(autouse=True)
def picks(db, players, weeks, teams):
    return [
        PickFactory.create_batch(
            size=5,
            player=players[0],
            week=factory.Iterator(weeks),
            team=factory.Iterator(teams),
        ),
        PickFactory.create_batch(
            size=5,
            player=players[1],
            week=factory.Iterator(weeks),
            team=factory.Iterator(teams),
        ),
    ]


@pytest.fixture(autouse=True)
def player_statuses(db, players, seasons):
    return PlayerStatusFactory.create_batch(
        size=2, player=factory.Iterator(players), season=seasons[1]
    )
