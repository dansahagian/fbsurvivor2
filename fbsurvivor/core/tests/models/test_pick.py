from fbsurvivor.core.models import Pick


def test_pick_for_player_season(db, players, seasons, picks):
    queryset = Pick.objects.for_player_season(players[0], seasons[1])
    assert queryset.count() == 5
    assert list(queryset) == picks[0]


def test_pick_for_player_season_locked(db, players, seasons, picks):
    queryset = Pick.objects.for_player_season_locked(players[0], seasons[1])
    assert queryset.count() == 4
    assert list(queryset) == picks[0][:4]


def test_pick_for_result(db, weeks):
    queryset = Pick.objects.for_results(weeks[1])
    assert queryset.count() == 2
