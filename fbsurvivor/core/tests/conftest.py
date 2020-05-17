import datetime

import factory
import pytest

from fbsurvivor.core.tests.factories import (
    PlayerFactory,
    PlayerStatusFactory,
    SeasonFactory,
    WeekFactory,
    PickFactory,
    TeamFactory,
)
from fbsurvivor.core.utils import get_localized_right_now


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
    now = get_localized_right_now()
    nw = now + datetime.timedelta(days=7)
    lw = now - datetime.timedelta(days=7)
    ly = now - datetime.timedelta(days=365)

    return {
        "this_season": WeekFactory.create_batch(
            size=5,
            season=seasons[1],
            week_num=factory.Iterator([1, 2, 3, 4, 5]),
            lock_datetime=factory.Iterator([lw, lw, lw, lw, nw]),
        ),
        "last_season": WeekFactory.create_batch(
            size=5,
            season=seasons[0],
            week_num=factory.Iterator([1, 2, 3, 4, 5]),
            lock_datetime=ly,
        ),
    }


@pytest.fixture(autouse=True)
def teams(db, seasons):
    return {
        "this_season": TeamFactory.create_batch(
            size=5,
            season=seasons[1],
            team_code=factory.Iterator(["NE", "SF", "TB", "GB", "DAL"]),
            bye_week=factory.Iterator([1, 1, 2, 2, 3]),
        ),
        "last_season": TeamFactory.create_batch(
            size=5,
            season=seasons[0],
            team_code=factory.Iterator(["NE", "SF", "TB", "GB", "DAL"]),
            bye_week=factory.Iterator([1, 1, 2, 2, 3]),
        ),
    }


@pytest.fixture(autouse=True)
def picks(db, players, weeks, teams):
    seasons = ["this_season", "last_season"]
    return {
        "p1": {x: _picks(players[0], weeks[x], teams[x]) for x in seasons},
        "p2": {x: _picks(players[1], weeks[x], reversed(teams[x])) for x in seasons},
    }


@pytest.fixture(autouse=True)
def player_statuses(db, players, seasons):
    return {
        "p1": PlayerStatusFactory.create_batch(
            size=2, player=players[0], season=factory.Iterator(seasons)
        ),
        "p2": PlayerStatusFactory.create_batch(
            size=2, player=players[1], season=factory.Iterator(seasons)
        ),
    }


def _picks(player, weeks, teams):
    return PickFactory.create_batch(
        size=5,
        player=player,
        week=factory.Iterator(weeks),
        team=factory.Iterator(teams),
    )
