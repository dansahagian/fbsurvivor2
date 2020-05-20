from fbsurvivor.core.models import Pick


def test_pick_for_player_season(db, players, seasons, picks):
    p1 = players[0]
    this_season = seasons[1]

    qs = Pick.objects.for_player_season(p1, this_season)

    assert list(qs) == picks["p1"]["this_season"]


def test_pick_for_player_season_locked(db, players, seasons, picks):
    p1 = players[0]
    this_season = seasons[1]

    qs = Pick.objects.for_board(p1, this_season)

    assert list(qs) == picks["p1"]["this_season"][:4]  # last pick isn't locked


def test_pick_for_results(db, weeks, picks):
    first_week = weeks["this_season"][0]
    team1 = picks["p1"]["this_season"][0].team.team_code
    team2 = picks["p2"]["this_season"][0].team.team_code

    qs = Pick.objects.for_results(first_week)
    assert list(qs) == sorted([team1, team2])


def test_pick_for_result_updates(db, weeks, picks):
    first_week = weeks["this_season"][0]
    team = picks["p1"]["this_season"][0].team

    qs = Pick.objects.for_result_updates(first_week, team)
    assert qs.count() == 1
