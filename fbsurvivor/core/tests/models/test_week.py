import pytest

from fbsurvivor.core.models import Week


@pytest.fixture
def this_season(seasons):
    return seasons[1]


def test_week_for_display(this_season, weeks):
    qs = Week.objects.for_display(this_season)
    assert list(qs) == weeks["this_season"][:4]


def test_week_get_current(this_season, weeks):
    qs = Week.objects.get_current(this_season)
    assert qs == weeks["this_season"][3]


def test_week_get_next(this_season, weeks):
    qs = Week.objects.get_next(this_season)
    assert qs == weeks["this_season"][4]


def test_week_is_locked(weeks):
    assert weeks["this_season"][3].is_locked
    assert not weeks["this_season"][4].is_locked
